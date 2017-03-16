'use strict';

W.ns('W.pages.strain');

W.pages.strain.StrainsRootPage = Class.extend({

    currentPage: 0,
    pageSize: 8,
    strains: [],

    ui: {
        $pageSelector: $('.page-num'),
        $nextPage: $('.next-page'),
        $prevPage: $('.prev-page')
    },

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
                that.initPager();
            });
        }
    },

    getStrainsByType: function getStrainsByType(type, success) {
        $.ajax({
            method: 'GET',
            url: '/api/v1/search/strains/{0}?limit={1}'.format(type, 40),
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
    },

    initPager: function initPager() {
        var that = this;

        this.ui.$prevPage.on('click', function (e) {
            e.preventDefault();

            var $currentActivePage = $('.page-num.active'),
                nextPageNum = parseInt($currentActivePage.text(), 10) - 1;

            if (nextPageNum >= 1) {
                that.currentPage = nextPageNum - 1;
                $currentActivePage.removeClass('active');
                $currentActivePage.prev().addClass('active');
                that.regions.$strainsList.html('');
                that.showStrains();
            }
        });

        this.ui.$nextPage.on('click', function (e) {
            e.preventDefault();

            var $currentActivePage = $('.page-num.active'),
                nextPageNum = parseInt($currentActivePage.text(), 10) - 1;

            if (nextPageNum < 4) {
                that.currentPage = nextPageNum + 1;
                $currentActivePage.removeClass('active');
                $currentActivePage.next().addClass('active');
                that.regions.$strainsList.html('');
                that.showStrains();
            }
        });

        this.ui.$pageSelector.on('click', function (e) {
            e.preventDefault();

            var $selectedPage = $(this);

            that.ui.$pageSelector.removeClass('active');
            $selectedPage.addClass('active');

            that.currentPage = parseInt($selectedPage.text(), 10) - 1; // -1 because initial page num is 0
            that.regions.$strainsList.html('');
            that.showStrains();
        });
    }

});