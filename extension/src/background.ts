// Copyright 2020-present Kensho Technologies, LLC.
import 'core-js/stable';
import 'regenerator-runtime/runtime';
import languagePluginLoader from './python/pyodide.js';
import MyPythonScript from './python/MyPythonScript.py';

(() => {
  const browser = window.chrome || window.browser;
  const MODELS = [
    'cv.joblib',
    'df_articles.csv',
    'wwt_config.json',
    'xbm25.npz',
  ];
  const MODELS_BASE_URL = browser.runtime.getURL('models');

  const initialized = {
    models: false,
    contextMenus: false,
  };

  // load models
  const MODELS_BIN = {};
  (async () => {
    await Promise.all(
      MODELS.map(async (uri) => {
        MODELS_BIN[uri] = await (
          await fetch(`${MODELS_BASE_URL}/${uri}`)
        ).arrayBuffer();
      })
    );

    // make sure the plugin loader has resolved
    await languagePluginLoader;
    await pyodide.loadPackage(['nltk', 'numpy', 'pandas', 'scikit-learn']);
    await pyodide.runPythonAsync(MyPythonScript);

    // forward the data to the script
    const set_model_file_data = pyodide.pyimport('set_model_file_data');
    Object.entries(MODELS_BIN).forEach(([uri, data]) =>
      set_model_file_data(uri, data)
    );

    initialized.models = true;
    console.debug('WikiWhatsThis - READY!');
  })();

  // configure listeners
  browser.extension.onMessage.addListener((request, sender, callback) => {
    switch (request.action) {
      case 'initialize': {
        initContextMenu();
        break;
      }
    }
  });

  function initContextMenu() {
    if (initialized.contextMenus) return;

    browser.contextMenus.create({
      id: 'suggest',
      title: 'WikiWhatsThis - Suggest',
      contexts: ['selection'],
    });

    browser.contextMenus.onClicked.addListener(async (info, tab) => {
      if (info.menuItemId !== 'suggest') return;

      // forward the selectedText to the python script
      const search = pyodide.pyimport('search');
      const result = search(info.selectionText);

      browser.tabs.sendMessage(tab.id, {
        action: 'suggest',
        query: info.selectionText,
        result: JSON.parse(result),
      });
    });

    initialized.contextMenus = true;
  }
})();
