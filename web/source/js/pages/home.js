'use strict';

W.ns('W.pages');

W.pages.HomePage = Class.extend({

    ui: {
        $userLocationBtn: $('.your-location')
    },

    init: function init(options) {
        this.location = options && options.location;
        this.authenticated = options && options.authenticated;
        this.userId = options && options.userId;

        this.initStrainLookupField();
        this.updateLocation();
    },

    initStrainLookupField: function initStrainLookupField() {
        var lookupTemplate = _.template($('#strain-lookup-field').html());
        $('.strain-name-field').html(lookupTemplate({
            'lookup_placeholder': 'Blue Dream, Maui Wowie, Pineapple express ...'
        }));
        new W.pages.strain.StrainLookup({ onSelect: this.navigateToStrainDetailPage });
    },

    navigateToStrainDetailPage: function navigateToStrainDetailPage(selected) {
        if (selected.variety && selected.slug) {
            window.location.href = '/strains/{0}/{1}/'.format(selected.variety, selected.slug);
        }
    },

    updateLocation: function updateLocation() {
        this.ui.$userLocationBtn.on('click', function () {
            W.Location.init({
                location: null,
                authenticated: this.authenticated,
                userId: this.userId
            });
        });
    }
});
