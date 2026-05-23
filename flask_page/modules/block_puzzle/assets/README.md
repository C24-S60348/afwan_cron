# Block Puzzle Assets

Copy the PNG image assets from the original blockpuzzle service to this directory.

These files are served at `/block-puzzle/assets/<filename>`.

Required files:
- `btnlocalmultiplayer.png`
- `btnmultiplayeronline.png`
- `finalUIMainmenu.png`
- `leftmainmenuroadwithcars.png`
- `maindescription.png`
- `maininfobutton.png`
- `maintitle.png`
- `rightbelowmainmenutrafficwithroad.png`
- `titledescandinfobtn.png`

On the server, copy them from the original blockpuzzle directory:
```bash
cp /home/afwanhaziq/blockpuzzle/assets/*.png flask_page/modules/block_puzzle/assets/
```
