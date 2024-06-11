const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  outputDir: 'dist',
  publicPath: './',
  assetsDir: 'static',
  configureWebpack: {
    devtool: 'source-map'
  },

  chainWebpack: (config) => {
    // Tilføj denne konfiguration for at indstille tegnsættet til UTF-8
    config.plugin('html').tap((args) => {
      args[0].charset = 'latin1';
      return args;
    });

    // Fjern prefetch-plugin'en
    config.plugins.delete('prefetch');
  },
})