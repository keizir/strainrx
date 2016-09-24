/*
 *   JS to support base.html
 */
'use strict';

W.ns('W');

W.Base = function () {

    var ctx = {},
        BaseView = W.views.BaseView;

    return {
        init: function init() {
            new BaseView(ctx);
        }
    };
}();
