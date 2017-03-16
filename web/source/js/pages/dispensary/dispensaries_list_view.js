'use strict';

W.ns('W.pages.dispensary');

W.pages.dispensary.DispensariesListView = function () {

    var DispensariesList = W.pages.dispensary.DispensariesList;

    return {
        init: function init(options) {
            new DispensariesList(options);
        }
    };
}();
