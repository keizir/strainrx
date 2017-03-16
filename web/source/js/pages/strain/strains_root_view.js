'use strict';

W.ns('W.pages.strain');

W.pages.strain.StrainsRootView = function () {

    var StrainsRootPage = W.pages.strain.StrainsRootPage;

    return {
        init: function (options) {
            new StrainsRootPage(options);
        }
    };
}();
