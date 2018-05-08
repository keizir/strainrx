'use strict';

W.ns('W.pages.strain');

W.pages.strain.StrainDetailView = function () {

    var StrainDetailPage = W.pages.strain.StrainDetailPage;

    return {
        init: function (options) {
            new StrainDetailPage(options);
        }
    };
}();
