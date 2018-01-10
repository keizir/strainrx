'use strict';

W.ns('W.pages.grower');

W.pages.grower.GrowerInfo = Class.extend({
    init: function init() {
        this.attachEventHandlers();
    },

    attachEventHandlers: function attachHandlers() {
        $('.filter').on('click', this.onFilterClick);
    },

    onFilterClick: function onFilterClick(e) {
        var $currentTarget = $(e.currentTarget),
            $strain = $('.strain'),
            $strainPlaceholder = $('.strain-placeholder');

        var filter = $currentTarget.attr('data-filter');

        if (filter === 'all') {
            $strain.css('display', '');
            if ($strain.length === 0) {
                $strainPlaceholder.css('display', '');
            } else {
                $strainPlaceholder.css('display', 'none');
            }
        } else {
            $strain.css('display', 'none');
            $('.strain[data-variety="{0}"]'.format(filter)).css('display', '');

            if ($('.strain[data-variety="{0}"]'.format(filter)).length === 0) {
                $strainPlaceholder.css('display', '');
            } else {
                $strainPlaceholder.css('display', 'none');
            }
        }

        $('.filter.active').removeClass('active');
        $('.filter[data-filter="{0}"]'.format(filter)).addClass('active');
    }

});