'use strict';

W.ns('W.common');

W.common.Model = Class.extend({

    model: {},

    init: function init(model) {
        this.model = model || {};
    },

    get: function (key) {
        return this.model[key];
    },

    set: function (key, value) {
        this.model[key] = value;
    }
});
