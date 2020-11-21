// Copyright 2020-present Kensho Technologies, LLC.
const fs = require('fs');
const path = require('path');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin')

const IS_DEV = process.env.NODE_ENV !== 'production';
const ROOT_PATH = path.join(__dirname);
const PATHS = {
  ROOT: ROOT_PATH,
  OUT: `${ROOT_PATH}/webpack-${IS_DEV ? 'build' : 'dist'}`,
  DIST: `${ROOT_PATH}/webpack-dist`,
}

const nodeExternals = () => fs.readdirSync('node_modules').reduce((acc, mod) => {
  if (['.bin'].indexOf(mod) !== -1) return acc;
  acc[mod] = 'commonjs ' + mod;
  return acc;
}, {});

module.exports = {
  context: ROOT_PATH,
  mode: !IS_DEV ? 'production' : 'development',
  devtool: IS_DEV ? 'inline-source-map' : undefined,
  entry: {
    content: './src/content.ts',
    background: './src/background.ts',
  },
  target: 'node',
  externals: nodeExternals(),
  resolve: {
    modules: ['src', 'node_modules'],
    extensions: ['.js', '.json', '.ts'],
  },
  output: {
    path: PATHS.OUT,
    filename: '[name].js',
  },
  module: {
    rules: [
      {
        test: /\.[jt]s$/,
        exclude: /node_modules/,
        loader: 'babel-loader',
        options: {
          cacheDirectory: true,
          presets: ['@babel/preset-env', '@babel/preset-typescript'].filter(Boolean),
          plugins: ['@babel/plugin-proposal-class-properties'].filter(Boolean),
        },
      },
      {
        test: /\.(py|css)$/i,
        loader: 'raw-loader',
      }
    ],
  },
  plugins: [
    new CleanWebpackPlugin(),
    new CopyWebpackPlugin({
      patterns: [{from: 'public'}],
    })
  ],
};
