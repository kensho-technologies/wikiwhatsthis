// Copyright 2020-present Kensho Technologies, LLC.
import 'core-js/stable';
import 'regenerator-runtime/runtime';
import {IResult} from './definitions/IResult';
import ResultsTemplate from './templates/results';

(() => {
  const browser = window.chrome || window.browser;
  const BASE_URL = browser.runtime.getURL('/');
  browser.extension.sendMessage({action: 'initialize'});

  browser.extension.onMessage.addListener(
    ({
      action,
      query,
      result,
    }: {
      action: string;
      query: string;
      result: IResult[];
    }) => {
      switch (action) {
        case 'suggest': {
          const newWindow = window.open(
            'about:blank',
            'WikiWhatsThis - Results',
            'width=640, height=680',
            true
          );
          newWindow.document.write(ResultsTemplate(query, result, BASE_URL));
          break;
        }
      }
    }
  );
})();
