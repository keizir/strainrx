'use strict';

W.ns('W.pages.grower');

W.pages.grower.GrowerInfoView = function () {

    var GrowerInfo = W.pages.grower.GrowerInfo;

    return {
        init: function () {
            new GrowerInfo();
        }
    };
}();
