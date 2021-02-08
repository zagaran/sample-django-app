const path = require('path')
const BundleTracker = require('webpack-bundle-tracker')


/**
 * Entry point configuration.
 *
 * This is where you should configure your webpack entry points, for example, a different entry point per page.
 */

const ENTRIES = {
  Home: './src/Pages/Home.js',
  Hello: './src/Components/Hello.js'
}

const SHARED_ENTRIES = [
  './node_modules/react-app-polyfill/ie11.js',
]

/**
 * nwb config
 */
module.exports = function({command}) {

  /* Set config */
  const config = {
    type: 'react-app',
  }
  config.webpack = {
    config(webpackConfig) {

      // Set new entry configuration
      webpackConfig.entry = {}
      Object.keys(ENTRIES).forEach((entryKey) => {
        webpackConfig.entry[entryKey] = [...SHARED_ENTRIES, ENTRIES[entryKey]]
      })
      return webpackConfig
    },
    extra: {
      output: {
        filename: '[name].js',
        chunkFilename: '[name].js',
        path: path.resolve('./static/webpack_bundles/'),
      },
      module: {
        rules: [
          {
            test: /\.js$/,
            loader: 'babel-loader',
            include: /node_modules/,
            options: {
              // babelrc: false,
              // cacheDirectory: true,
              presets: [
                ['@babel/preset-env', {'loose': true, 'modules': false,}],
                ['@babel/preset-react', {'development': false}],
                ['babel-preset-proposals', {
                  'loose': true,
                  'decorators': true,
                  'classProperties': true,
                  'exportDefaultFrom': true,
                  'exportNamespaceFrom': true,
                  'absolutePaths': true,
                }],
              ],
              plugins: [
                '@babel/plugin-transform-react-constant-elements',
                'babel-plugin-transform-react-remove-prop-types',
                ['@babel/plugin-transform-runtime', {useESModules: true,}],
                '@babel/plugin-syntax-dynamic-import',
                '@babel/plugin-transform-modules-commonjs',
              ],
            },
          },
          {
            test: /\.js$/,
            exclude: /node_modules/,
            loader: 'django-react-loader',
          },
        ],
      },
      plugins: [
        new BundleTracker({filename: './webpack-stats.json'}),
      ],
    },
    publicPath: '/static/webpack_bundles/',
  }
  return config
}
