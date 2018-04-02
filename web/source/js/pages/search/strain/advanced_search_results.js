'use strict';

W.ns('W.pages');

W.pages.AdvancedSearchResultsPage = Class.extend({

    scrollPage: 1,
    scrollSize: 20,
    sortKey: 'sort',
    searchResultsTotal: 0,

    ui: {
        $document: $(document),
        $window: $(window),

        $searchHeader: $('.search-result-header-wrapper'),
        $searchResultFooterRegion: $('.search-result-footer-wrapper'),
        $menuLinkWrapper: $('.filter-menu-wrapper'),
        $menuLink: $('.filter-menu-wrapper input[type="checkbox"]'),

        $searchResult: $('.search-result'),
        $loadingIcon: $('.scroll-icon i'),
        resultItem: '.result-item'
    },

    init: function (options) {
        var that = this;
        this.name = 'AdvancedSearchResultsPage';
        this.isEmailVerified = options.isEmailVerified;
        this.currentUserId = options.currentUserId;
        this.search = new URLSearchParams(window.location.search);

        this.getSearchResults(function () {
            that.buildResultsFilterMenu();

            that.ui.$searchHeader.removeClass('hidden');
            if (!that.currentUserId) {
                that.showLoginDialog();
            } else if (!that.isEmailVerified) {
                that.showVerifyDialog();
            }
        });

        W.subscribe.apply(this);
    },

    showLoginDialog: function showLoginDialog() {
        $('#results-ready-dialog').css('display', 'initial');
    },

    showVerifyDialog: function showVerifyDialog() {
        $('#email-verify-dialog').css('display', 'initial');

        var callApi = function() {
            var firstParagraph = $('#email-verify-dialog p:first-of-type');
            firstParagraph.text('Sending email..');

            $.ajax({
                method: 'GET',
                url: '/api/v1/users/resend-email-confirmation'
            }).success(function() {
                firstParagraph.text('Email sent successfully.');
            }).fail(function() {
                firstParagraph.html(
                    "There was a problem with sending your email.\n" +
                    '<a id="resend-email-link" href="#">Click here</a> to resend it.'
                );
                $('#resend-email-link').on('click', callApi);
            });
        };

        $('#resend-email-link').on('click', callApi);
    },

    getSearchResults: function getSearchResults(success) {
        var that = this;
        this.ui.$loadingIcon.addClass('rotating');

        $.ajax({
            method: 'GET',
            url: '/api/v1/search/search/?{0}&page={1}&size={2}'
                .format(window.location.search.slice(1), that.scrollPage, that.scrollSize),
            dataType: 'json',
            error: function () {
                that.ui.$searchHeader.addClass('hidden');
                that.ui.$searchResultFooterRegion.addClass('hidden');
                that.ui.$searchResult.append(
                    '<div class="search-result-subtitle">There was an error processing your request please try again at a later</div>');
            },
            success: function (data) {
                var searchResults = data.payloads;

                that.searchResultsTotal = data.total;
                that.ui.$searchResultFooterRegion.addClass('hidden');

                if (searchResults.length === 0 && that.searchResultsTotal === 0) {
                    that.ui.$searchResult.append('<div class="search-result-subtitle">No Results Found</div>');
                } else {

                    for (var i = 0; i < searchResults.length; i++) {
                        var position = '{0}{1}'.format(that.scrollPage, i);

                        that.ui.$searchResult.append(that.parseSearchResultItem(position, searchResults[i]));
                    }

                    that.ui.$loadingIcon.removeClass('rotating');
                    that.scrollPage += 1;

                    if (success) {
                        success();
                    }
                }

                that.totalResultCount = $(that.ui.resultItem).length;
                that.handleScrollPage();
            }
        });

        setTimeout(function () {
            $('#loading-spinner').hide();
        }, 500);
    },

    buildResultsFilterMenu: function buildResultsFilterMenu() {
        var that = this,
            currentFilter = that.search.getAll(that.sortKey);
        currentFilter = currentFilter.length ? currentFilter : [''];

        $.each(that.ui.$menuLink, function () {
            var $el = $(this);

            if (currentFilter.indexOf($el.val()) !== -1) {
                $el.prop("checked", true);
                $el.parents('.form-field').addClass('active');
            } else {
                $el.prop("checked", false);
                $el.parents('.form-field').removeClass('active');
            }
        });

        that.ui.$menuLinkWrapper.on('change', 'input[type="checkbox"]', function (e) {
            e.preventDefault();
            that.search.delete(that.sortKey);

            $.each(that.ui.$menuLink, function () {
                var $el = $(this);

                if ($el.is(':checked')){
                    $el.parents('.form-field').addClass('active');
                    that.search.append(that.sortKey, $el.val());
                } else {
                    $el.parents('.form-field').removeClass('active');
                }
            });

            window.history.pushState({}, '', '?' + that.search.toString());
            that.applyNewFilter();
        });
    },

    applyNewFilter: function applyNewFilter() {
        this.scrollPage = 1;
        this.ui.$searchResult.empty();
        this.ui.$searchResultFooterRegion.removeClass('hidden');
        this.getSearchResults();
    },

    handleScrollPage: function () {
        var that = this;

        this.ui.$window.on('scroll', function () {
            if (that.ui.$window.scrollTop() >= (that.ui.$document.height() - that.ui.$window.height()) * 0.6 &&
                that.searchResultsTotal > that.totalResultCount) {

                that.ui.$window.off('scroll');
                that.getSearchResults();
            }
        });
    },

    parseSearchResultItem: function (position, item) {
        var that = this,
            compiled = _.template($('#strain-item-template').html());

        return compiled({
            'obfuscated': !Boolean(that.currentUserId) || !that.isEmailVerified,
            'position': position,
            'strain': item,
            'closestDistance': that.findClosestDistance
        });
    },

    findClosestDistance: function findClosestDistance(locations) {
        var distances = [], min;
        if (locations && locations.length > 0) {
            for (var i = 0; i < locations.length; i++) {
                distances.push(locations[i].distance);
            }
            min = Math.min.apply(Math, distances);
            return 'Nearest {0}mi'.format(Math.round(min * 100) / 100);
        }
    },

    formatDistance: function formatDistance(d) {
        return '({0}mi)'.format(Math.round(d * 100) / 100);
    },

    formatPrice: function formatPrice(p) {
        return p ? '${0}'.format(p) : 'n/a';
    }
});
