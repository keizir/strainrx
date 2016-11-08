'use strict';

W.ns('W.pages');

W.pages.HomePage = Class.extend({

    init: function init() {
        this.initStrainLookupField();
        this.clickLookupSubmit();
    },

    initStrainLookupField: function initStrainLookupField() {
        var lookupTemplate = _.template($('#strain-lookup-field').html());
        $('.strain-name-field').html(lookupTemplate({
            'lookup_placeholder': 'Example: Blue Dream, Maiu Wowie, Pineapple express'
        }));
        new W.pages.strain.StrainLookup();
    },

    clickLookupSubmit: function clickLookupSubmit() {
        var that = this;
        $('.lookup-submit').on('click', function (e) {
            e.preventDefault();
            var $input = $('.lookup-input'),
                strainName = $input.val(),
                strainSlug = $input.attr('payload-slug');

            if (strainName && strainSlug) {
                window.location.href = '/search/strain/{0}'.format(strainSlug);
            }
        });
    }
});
