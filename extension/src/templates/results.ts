// Copyright 2020-present Kensho Technologies, LLC.
import {IResult} from '../definitions/IResult';
import css from './results.css';

const WIKI_BASE_URL = 'https://en.wikipedia.org/wiki';

export default function ResultTemplate(
  query: string,
  result: IResult[],
  publicURL = ''
) {
  console.log({query, result});
  return `
    <!DOCTYPE html>
    <html>
      <head>
        <title>WikiWhatsThis - Results</title>
        <style>
          ${css}
        </style>
      </head>
      <body>
        <header class="header">
          <img class="header-logo" src="${publicURL}icon.png" /> WikiWhats<span class="logo-this">This</span> <span class="header-title">Results</span>
        </header>
        <pre class="query">
          <div class="query-title">Query</div>
          <div class="query-content">${query}</div>
        </pre>

        <section class="results">
          ${result.slice(0, 10).reduce((acc, result) => {
            acc += `
              <article class="result">
                <a href="${WIKI_BASE_URL}/${result.page_title}" target="_blank">
                  <div class="result-content">
                    <div class="result-title">${result.page_title}</div>
                    <div class="result-meta">
                      <span>🎯${result.score.toFixed(2)}</span>
                      <span>👁️${result.views}</span>
                    </div>
                  </div>
                  <div class="button">🔍</div>
                </a>
              </article>
            `;
            return acc;
          }, '')}
        </section>
      </body>
    </html>
  `;
}
