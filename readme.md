# 6502 Bresenham Sheared Ellipse

This project derives and implements a sheared Bresenham-style ellipse on a 6502 processor.

It uses only integer operations, and avoids any explicit sqrt calculations or multiplications within the main loop.

See [algorithm derivation](./algorithm_derivation/derivation.ipynb)

![Ellipse](./example.png)

## The 'OS Legal' Ellipse

Run Ellips2: [here in browser](https://bbc.godbolt.org/?autoboot&disc=https://raw.githubusercontent.com/TobyLobster/ellipse/main/ELLIPS2.SSD)

In this incarnation, rendering is done by regular calls to the operating system to draw points and lines.
A novel method is used to speed up rendering. We draw the longest straight lines that render identically to the individual pixels that would normally be drawn. See [rendering fewer lines](./fewer_lines.md) for more information.

## The 'Speedy' Ellipse

By using a 16 bit approximation of the ellipse algorithm, bypassing the OS and writing to screen memory directly, and using a custom screen mode that is 256 pixels wide we can speed up the rendering to interactive levels of frame rate. Also by [double buffering](https://en.wikipedia.org/wiki/Multiple_buffering#Double_buffering_in_computer_graphics) the screen we can get flicker free animation.

Run Ellips5: [here in browser](https://bbc.godbolt.org/?autoboot&disc=https://raw.githubusercontent.com/TobyLobster/ellipse/main/ELLIPS5.SSD)

Controls:

| Keys     | Effect                              |
| -------- | ----------------------------------- |
| Z and X  | change the length of one axis       |
| : and /  | change the length of the other axis |
| A and S  | change the angle of the ellipse     |

For speed of plotting, this ellipse algorithm exploits two symmetries in total (top-down, and left-right).  It calculates an axis-aligned ellipse (which creates the extra left-right symmetry), and then afterwards adds in the shear. Unfortunately this produces a less-than pixel-perfect extra wobble in the curve plotting, for angled ellipses, where the Bresenham straight-line algorithm's steps (of the central shear-line) interfere with Bresenham-style steps of the axis-aligned ellipse.  But it's twice as fast, and works well with 16-bit approximations for the axis-aligned ellipse.  [Basic version](https://bbcmic.ro/#%7B%22v%22%3A1%2C%22program%22%3A%2210MODE%204%5Cn20PROCellipse%28160%2C128%2C80%2C50%2C20%29%5Cn30END%5Cn40%3A%5Cn50DEFPROCellipse%28CX%25%2CCY%25%2CA%25%2CB%25%2CS%25%29%5Cn60VDU%2029%2CCX%25*4%3BCY%25*4%3B%5Cn70BB%25%3DB%25*B%25%3ABBdouble%25%3DBB%25*8%5Cn80AA%25%3DA%25*A%25%5Cn85ABB%25%3DA%25*BB%25%5Cn90%20SSpAAdouble%25%3DAA%25*8%3AAAB8%25%3DSSpAAdouble%25*B%25%5Cn120XW%25%3D%20A%25%3A%20REM%20%5C%22X%20Width%5C%22%20is%20horizontal%20half-width%20of%20ellipse%5Cn121T2%25%3DA%25*B%25*2%2BB%25%3ADR%25%3DBB%25%2BABB%25*4%3AFR%25%3D%28B%25*T2%25-BB%25%29*4%3AdDR%25%3DAA%25*4%5Cn122ROR%25%3D2%5Cn125IF%20ABS%28FR%25%29%3E2%5E15%20OR%20ABS%28dDR%25%29%3E2%5E15%20OR%20ABS%28AAB8%25%29%3E2%5E15%3ABBdouble%25%3DBBdouble%25DIVROR%25%3A%20SSpAAdouble%25%3DSSpAAdouble%25DIVROR%25%3ADR%25%3DDR%25DIVROR%25%3AFR%25%3DFR%25DIVROR%25%3AdDR%25%3DdDR%25DIVROR%25%3AAAB8%25%3DAAB8%25DIV2%3AGOTO125%3AREM%20reduce%20everything%20down%20to%2016%20bits%20%28losing%20some%20accuracy!%29%5Cn130EC%25%3DB%25DIV2%3AXC%25%3D0%5Cn131OXR%25%3DA%25%3AOXL%25%3D-A%25%5Cn140FOR%20Y%25%3D0%20TO%20B%25-1%5Cn220%3A%5Cn240IF%20DR%25-FR%25%20%3E%200%20AND%20XW%25%3E0%20PROCdec_xw%3AGOTO%20240%3AREM%20main%20iteration%20to%20solve%20the%20sqrt%5Cn260%3A%5Cn265XR%25%3DXC%25%2BXW%25%5Cn270DX%25%3DSGN%28XR%25-OXR%25%29%20%3AREM%20this%20%2BXC%25%20adds%20the%20shear%20back%20in%20now%5Cn280MOVE%20%20%28OXR%25%2BDX%25%29*4%2C%20Y%25*4%3ADRAW%20XR%25*4%2C%20Y%25*4%5Cn290MOVE%20-%28OXR%25%2BDX%25%29*4%2C-Y%25*4%3ADRAW%20-XR%25*4%2C-Y%25*4%5Cn380%3A%5Cn381XL%25%3DXC%25-XW%25%20%3AREM%20XL%20is%20symmetric%20to%20XR.%20%20No%20need%20to%20calculate%20it%20with%20an%20iteration!%5Cn390DX%25%3DSGN%28XL%25-OXL%25%29%20%3AREM%20this%20%2BXC%25%20adds%20the%20shear%20back%20in%20now%5Cn400MOVE%20%20%28OXL%25%2BDX%25%29*4%2C%20Y%25*4%3ADRAW%20XL%25*4%2C%20Y%25*4%5Cn410MOVE%20-%28OXL%25%2BDX%25%29*4%2C-Y%25*4%3ADRAW%20-XL%25*4%2C-Y%25*4%5Cn420%3A%5Cn421OXR%25%3DXR%25%3AOXL%25%3DXL%25%5Cn430EC%25%3DEC%25%2BABS%28S%25%29%5Cn435%3A%5Cn440IF%20EC%25%3EB%25%3AXC%25%3DXC%25%2BSGN%28S%25%29%3AEC%25%3DEC%25-B%25%3AGOTO440%3AREM%20this%20is%20a%20bresenham%20straight-line%20loop%2C%20for%20the%20centre%20line%20XC%25%5Cn450DR%25%3DDR%25%2BdDR%25%5Cn455dDR%25%3DdDR%25%2BSSpAAdouble%25%5Cn480NEXT%5Cn490%3A%5Cn495REM%20finish%20of%20cap%20and%20tail%20hlines%20to%20ellipse%5Cn500DX%25%3DSGN%28XR%25-XL%25%29%3AY%25%3DB%25%5Cn510MOVE%20%20%28XL%25%2BDX%25%29*4%2C%20Y%25*4%3ADRAW%20%28XR%25-DX%25%29*4%2C%20Y%25*4%5Cn515MOVE%20-%28XL%25%2BDX%25%29*4%2C-Y%25*4%3ADRAW-%28XR%25-DX%25%29*4%2C-Y%25*4%5Cn520%3A%5Cn530ENDPROC%5Cn540%3A%5Cn580DEFPROCdec_xw%3AXW%25%3DXW%25-1%3ADR%25%3DDR%25-FR%25%3AFR%25%3DFR%25-BBdouble%25%3AENDPROC%3AREM%20don't%20need%20IC%25%5Cn%22%7D)

## Versions

A progression of versions is presented:

| version | execute in browser | time (centiseconds) | notes                    |
| ------- | ------------------ | ------------------: | ------------------------ |
| Ellips0 | [here in browser](https://bbc.godbolt.org/?autoboot&disc=https://raw.githubusercontent.com/TobyLobster/ellipse/main/ELLIPS0.SSD) | 70cs | Draws individual pixels using the Operating System to do so. |
| Ellips1 | [here in browser](https://bbc.godbolt.org/?autoboot&disc=https://raw.githubusercontent.com/TobyLobster/ellipse/main/ELLIPS1.SSD) | 61cs | Draws horizontal, vertical and 45 degree lines using the Operating System to do so. |
| Ellips2 | [here in browser](https://bbc.godbolt.org/?autoboot&disc=https://raw.githubusercontent.com/TobyLobster/ellipse/main/ELLIPS2.SSD) | 48cs | Draws lines of all angles using the Operating System to do so. See [rendering fewer lines](./fewer_lines.md). |
| Ellips3 | [here in browser](https://bbc.godbolt.org/?autoboot&disc=https://raw.githubusercontent.com/TobyLobster/ellipse/main/ELLIPS3.SSD) | 24cs | Writes individual bytes directly to screen memory... |
| Ellips4 | [here in browser](https://bbc.godbolt.org/?autoboot&disc=https://raw.githubusercontent.com/TobyLobster/ellipse/main/ELLIPS4.SSD) |  8cs | ... and uses an approximate ellipse using only 16 bit arithmetic in the main loop |
| Ellips5 | [here in browser](https://bbc.godbolt.org/?autoboot&disc=https://raw.githubusercontent.com/TobyLobster/ellipse/main/ELLIPS5.SSD) |  8cs | ... and made interactive (see controls above) |

## Theoretical Timings

To get an idea of what overhead the OS has, we render 65 straight lines (hardcoded) (a) using the OS, and (b) using the line drawing routine from Elite.
These programs don't know how to draw an ellipse, they are just a hardcoded set of lines used as a simple rendering test.

| version | execute in browser | time (centiseconds) | notes                    |
| ------- | ------------------ | ------------------: | ------------------------ |
| EllipsX | [here in browser](https://bbc.godbolt.org/?autoboot&disc=https://raw.githubusercontent.com/TobyLobster/ellipse/main/ELLIPSX.SSD) | 14cs | Draws 65 lines using the OS, as a test of how fast it could go in theory. |
| EllipsY | [here in browser](https://bbc.godbolt.org/?autoboot&disc=https://raw.githubusercontent.com/TobyLobster/ellipse/main/ELLIPSY.SSD) |  3cs | Draws 65 lines using the Elite line drawing code, as a test of how fast it could go in theory. |
