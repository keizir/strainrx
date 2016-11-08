'use strict';

W.ns('W.common');

W.common.Dialog = function ($el, closeCallback) {
    if ($el) {

        $el.removeClass('hidden');
        $el.dialog({
            closeOnEscape: true,
            height: 450,
            width: 'auto',
            modal: true,
            draggable: false,
            resizable: false,
            create: function () {
                $(this).css("maxWidth", "450px");
            },
            close: function (e, ui) {
                if (closeCallback) {
                    closeCallback(e, ui);
                }
            }
        });
    }
};

W.common.ConfirmDialog = function ($el, closeCallback) {
    if ($el) {

        $el.removeClass('hidden');
        $el.dialog({
            closeOnEscape: true,
            height: 200,
            width: 'auto',
            modal: true,
            draggable: false,
            resizable: false,
            create: function () {
                $(this).css("maxWidth", "450px");
            },
            close: function (e, ui) {
                if (closeCallback) {
                    closeCallback(e, ui);
                }
            }
        });
    }
};
