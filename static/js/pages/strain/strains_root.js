'use strict';

W.ns('W.pages.strain');

W.pages.strain.StrainsRootPage = Class.extend({

    currentPage: 0,
    pageSize: 8,
    strains: [],

    regions: {
        $strainsList: $('.list')
    },

    templates: {
        strainExampleItem: _.template($('#strains_example_item_template').html())
    },

    init: function init(options) {
        var that = this;

        if (options && options.type) {
            that.getStrainsByType(options.type, function (data) {
                that.strains = data;
                that.regions.$strainsList.html('');
                that.showStrains();
            });
        }
    },

    getStrainsByType: function getStrainsByType(type, success) {
        $.ajax({
            method: 'GET',
            url: '/api/v1/search/strains/{0}?limit={1}'.format(type, 8),
            success: function (data) {
                success(data);
            }
        });
    },

    showStrains: function showStrains() {
        var that = this,
            start = this.currentPage * this.pageSize,
            page = this.strains.slice(start, start + this.pageSize),
            varieties = W.common.Constants.strainVarieties,
            Strain = this.templates.strainExampleItem;

        $.each(page, function (i, e) {
            that.regions.$strainsList.append(Strain({
                image: e.image,
                name: e.name,
                variety: e.variety,
                varietyName: varieties[e.variety],
                slug: e.slug
            }));
        });
    }

});