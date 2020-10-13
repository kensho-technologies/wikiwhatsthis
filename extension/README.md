# WikiWhatsThis Browser Extension

Tested with,

```bash
> npm -v 
6.14.8
> node -v 
v12.19.0
```

## Development Setup
```bash
git clone https://github.com/galtay/wikiwhatsthis.git
cd wikiwhatsthis/extension
npm install
```

## Beta Users
```bash
npm run update
npm run build
```

Navigate to `chrome://extensions` in your Chrome browser.
Turn on developer mode using the toggle in the upper right.
Click the `Load unpacked` button in the upper left. 
Point the file finder that opens to the `wikiwhatsthis/extension/.webpack.dist` directory (note that this is a hidden directory so you may have to toggle something in your file browser to show hidden files/directories).
To monitor the loading of the extension click on `Inspect views background page`.
This might crash. If it does, click `Load unpacked` and give it another try.
The background page view should open a pop-up that shows logging messages. 
You may see some warning like `DevTools failed to load SourceMap` or sklearn warnings about version mismatch and inconsistent stop words. This is OK. 
The last message from extension loading is `reading xbm25.npz`.
Once this is complete, you should see the option `WikiWhatsThis - Suggest` when you right click on highlighted text in your browser. If you do not see this option, try reloading the tab or restarting the browser. 
Sometimes you have to right-click and ask for suggestions more than once before it works. 
If it does work, you will see a popup of suggested Wikipedia pages. 
If you've gotten this far, thank the computer development gods and yourself for being an awesome beta user :) 



## Commands
> 🔨<b>builds</b>&nbsp;&nbsp;&nbsp;&nbsp;
> 👀<b>watches</b>&nbsp;&nbsp;&nbsp;&nbsp;
> 📦<b>packages</b>&nbsp;&nbsp;&nbsp;&nbsp;

|                  |                                                     |
| :--------------- | :-------------------------------------------------- |
| `npm start`      | 🔨 and 👀 files to the `.webpack.build` directory     |
| `npm run build`  | 🔨 the 📦 extension to the `.webpack.dist` directory. |
| `npm run update` | Download the latest models and pyodide packages.    |
