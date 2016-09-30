'use strict';

W.ns('W.common');

W.common.Dialog = function ($el, closeCallback) {
    if ($el) {

        $el.removeClass('hidden');
        $el.dialog({
            closeOnEscape: true,
            height: 450,
            width: 450,
            modal: true,
            draggable: false,
            resizable: false,
            close: function (e, ui) {
                if (closeCallback) {
                    closeCallback(e,ui);
                }
            }
        });
    }
};
