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

## Versions

A progression of versions is presented:

| version | execute in browser | time (centiseconds) | notes                    |
| ------- | ------------------ | ------------------: | ------------------------ |
| Ellips0 | [here in browser](https://bbc.godbolt.org/?autoboot&disc=https://raw.githubusercontent.com/TobyLobster/ellipse/main/ELLIPS0.SSD) | 70cs | Draws individual pixels using the Operating System to do so. |
| Ellips1 | [here in browser](https://bbc.godbolt.org/?autoboot&disc=https://raw.githubusercontent.com/TobyLobster/ellipse/main/ELLIPS1.SSD) | 61cs | Draws horizontal, vertical and 45 degree lines using the Operating System to do so. |
| Ellips2 | [here in browser](https://bbc.godbolt.org/?autoboot&disc=https://raw.githubusercontent.com/TobyLobster/ellipse/main/ELLIPS2.SSD) | 48cs | Draws lines of all angles using the Operating System to do so. See [rendering fewer lines](./fewer_lines.md). |
| Ellips3 | [here in browser](https://bbc.godbolt.org/?autoboot&disc=https://raw.githubusercontent.com/TobyLobster/ellipse/main/ELLIPS3.SSD) | 24cs | Writes individual bytes directly to screen memory... |
| Ellips4 | [here in browser](https://bbc.godbolt.org/?autoboot&disc=https://raw.githubusercontent.com/TobyLobster/ellipse/main/ELLIPS4.SSD) |  8cs | ... and uses an approximate ellipse using only 16 bit arithmetic in the main loop |
| Ellips5 | [here in browser](https://bbc.godbolt.org/?autoboot&disc=https://raw.githubusercontent.com/TobyLobster/ellipse/main/ELLIPS5.SSD) |  8cs | ... and made interactive (see controls below) |

## Theoretical Timings

To get an idea of what overhead the OS has, we render 65 straight lines (hardcoded) (a) using the OS, and (b) using the line drawing routine from Elite.
These programs don't know how to draw an ellipse, they are just a hardcoded set of lines used as a simple rendering test.

| version | execute in browser | time (centiseconds) | notes                    |
| ------- | ------------------ | ------------------: | ------------------------ |
| EllipsX | [here in browser](https://bbc.godbolt.org/?autoboot&disc=https://raw.githubusercontent.com/TobyLobster/ellipse/main/ELLIPSX.SSD) | 14cs | Draws 65 lines using the OS, as a test of how fast it could go in theory. |
| EllipsY | [here in browser](https://bbc.godbolt.org/?autoboot&disc=https://raw.githubusercontent.com/TobyLobster/ellipse/main/ELLIPSY.SSD) |  3cs | Draws 65 lines using the Elite line drawing code, as a test of how fast it could go in theory. |
