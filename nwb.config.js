/*
 * START_FEATURE django_react
 */


const path = require('path')
const BundleTracker = require('webpack-bundle-tracker')


/**
 * Entry point configuration.
 *
 * This is where you should configure your webpack entry points, for example, a different entry point per page.
 */

const ENTRIES = {
  // TODO delete me; this is just a reference example
  Home: './src/Pages/Home.js',
  Hello: './src/Components/Hello.js'
}

const SHARED_ENTRIES = [
  // we have not included react-app-polyfill in this sample application because it is not technically required for
  // projects which do not require polyfill. However, we do recommend installing and uncommenting this line of code
  // for projects which will need to have guaranteed functionality on older browsers.
  // './node_modules/react-app-polyfill/ie11.js',
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

/*
 * END_FEATURE django_react
 */
