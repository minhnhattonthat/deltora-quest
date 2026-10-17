"""codepatch.py: VWF and other arm9 hooks (docs/re/text.md, docs/re/engine.md).

Hook code + width table go in the free tail of the ITCM autoload block (the game uses 0x7B00 of ITCM's 0x8000 bytes):
the block grows, and the autoload list and module params after it are shifted to match.
"""
import struct

from keystone import KS_ARCH_ARM, KS_MODE_ARM, Ks

ARM9 = 0x02000000
PARAMS = 0xB64                 # module params offset in arm9 (from the nitrocode footer)
ITCM = 0x01FF8000
ITCM_USED = 0x7B00
HOOK = ITCM + ITCM_USED        # 0x01FFFB00
ITCM_FREE = 0x8000 - ITCM_USED
NWIDTH = 0x200                 # width table covers codes 0-1FF; 0 = keep the window's fixed pitch

PUTPIXEL = 0x0204E0AC
LINEX = 0x0204D9C4
ADVANCE = 0x0204DFCC           # ldr r1, [sb, #0x40] after each glyph
PUTPIXEL_CALLS = (0x0204DEF8, 0x0204DF38, 0x0204DF7C, 0x0204DFBC)

# Original words at every site we overwrite (asserted, so a different revision fails at build time).
ORIG_WORDS = {ADVANCE: 0xE5991040, LINEX: 0xE92D4038}

HOOK_ASM = f"""
vwf_adv:                        @ replaces ldr r1,[sb,#0x40]; sp = renderer frame: [sp+0x10] index, [sp+0x1c] string
    ldr r0, [sp, #0x10]
    ldr r1, [sp, #0x1c]
    add r1, r1, r0, lsl #1
    ldrsh r0, [r1]
    cmp r0, #{NWIDTH}
    ldrlo r1, =widths
    ldrblo r1, [r1, r0]
    movhs r1, #0
    cmp r1, #0
    ldreq r1, [sb, #0x40]
    bx lr

putpixel_nz:                    @ glyph pixels of value 0 must not erase the previous (overlapping) glyph
    cmp r2, #0
    bxeq lr
    ldr pc, =0x{PUTPIXEL:08X}

linex:                          @ r0 window, r1 string, r2 length -> start x of the line (same rules as the original)
    push {{r4, r5, r6, lr}}
    mov r3, #0                  @ width in px
    mov ip, #0                  @ index
lx_loop:
    cmp ip, r2
    bhs lx_noend
    add r4, r1, ip, lsl #1
    ldrsh r4, [r4]
    cmp r4, #0
    blt lx_ctrl
    mov r5, #0
    cmp r4, #{NWIDTH}
    ldrlo r6, =widths
    ldrblo r5, [r6, r4]
    cmp r5, #0
    ldreq r5, [r0, #0x40]
    add r3, r3, r5
    b lx_next
lx_ctrl:
    cmn r4, #3                  @ FFFD end / FFFE page / FFFF newline: line done
    bge lx_done
    cmn r4, #12                 @ FFF4 half-pitch space
    ldreq r5, [r0, #0x40]
    addeq r3, r3, r5, asr #1
    cmn r4, #11                 @ FFF5, FFF6 count as a full pitch in the original
    cmnne r4, #10
    ldreq r5, [r0, #0x40]
    addeq r3, r3, r5
lx_next:
    add ip, ip, #1
    b lx_loop
lx_done:
    ldr r1, [r0, #0x38]
    cmp r1, #0
    rsbeq r0, r3, #0xff         @ right-aligned
    popeq {{r4, r5, r6, pc}}
    cmp r1, #1
    moveq r0, #0x80             @ centred
    subeq r0, r0, r3, asr #1
    movne r0, #0                @ left
    pop {{r4, r5, r6, pc}}
lx_noend:
    mov r0, #0                  @ no terminator within length: original returns 0
    pop {{r4, r5, r6, pc}}
.ltorg
widths:
"""

_ks = Ks(KS_ARCH_ARM, KS_MODE_ARM)


def asm(src, addr):
    enc, _ = _ks.asm(src, addr)
    return bytes(enc)


def branch(op, frm, to):
    """B/BL encoded by hand: keystone mis-encodes some conditional branches (skill note)."""
    off = (to - frm - 8) >> 2
    assert -(1 << 23) <= off < (1 << 23)
    return struct.pack("<I", (0xEA000000 if op == "b" else 0xEB000000) | (off & 0xFFFFFF))


def apply(arm9, widths):
    """arm9 (bytes) -> patched arm9 with the VWF. widths: NWIDTH bytes."""
    a = bytearray(arm9)
    for addr, word in ORIG_WORDS.items():
        got = struct.unpack_from("<I", a, addr - ARM9)[0]
        assert got == word, f"{addr:08X}: {got:08X} != {word:08X} (wrong revision?)"
    blob = asm(HOOK_ASM, HOOK)    # `widths:` is the last label, so the table starts right after the code
    assert len(widths) == NWIDTH
    blob += bytes(widths)
    assert len(blob) <= ITCM_FREE, f"hook blob {len(blob):#x} > free ITCM {ITCM_FREE:#x}"
    # label addresses: vwf_adv at HOOK; the others found by their first instructions
    lab = {"vwf_adv": HOOK}
    for name, first in (("putpixel_nz", "cmp r2, #0\nbxeq lr"), ("linex", "push {r4, r5, r6, lr}\nmov r3, #0")):
        i = blob.find(asm(first, 0))
        assert i >= 0 and i % 4 == 0
        lab[name] = HOOK + i
    # site patches
    struct.pack_into("<I", a, ADVANCE - ARM9, struct.unpack("<I", branch("bl", ADVANCE, lab["vwf_adv"]))[0])
    for site in PUTPIXEL_CALLS:
        assert a[site - ARM9:site - ARM9 + 4] == branch("bl", site, PUTPIXEL), f"{site:08X} is not bl putpixel"
        a[site - ARM9:site - ARM9 + 4] = branch("bl", site, lab["putpixel_nz"])
    a[LINEX - ARM9:LINEX - ARM9 + 4] = branch("b", LINEX, lab["linex"])
    return grow_itcm(bytes(a), blob)


def grow_itcm(arm9, blob):
    a = bytearray(arm9)
    al, al_end, al_start = struct.unpack_from("<3I", a, PARAMS)
    entries = list(struct.unpack_from(f"<{(al_end - al) // 4}I", a, al - ARM9))
    assert entries[0] == ITCM and entries[1] == ITCM_USED, entries
    at = al_start - ARM9 + ITCM_USED            # end of the ITCM block's source in the binary
    pad = blob + b"\0" * (-len(blob) % 4)
    a[at:at] = pad
    entries[1] += len(pad)
    struct.pack_into(f"<{len(entries)}I", a, al - ARM9 + len(pad), *entries)
    struct.pack_into("<2I", a, PARAMS, al + len(pad), al_end + len(pad))
    return bytes(a)
