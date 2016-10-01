'use strict';

W.ns('W.pages');

W.pages.StrainSearchResultsPage = Class.extend({

    scrollPage: 0,

    ui: {
        $document: $(document),
        $window: $(window),
        $searchResultFooterRegion: $('.search-result-footer-wrapper')
    },

    init: function () {
        this.handleScrollPage();
    },

    handleScrollPage: function () {
        var that = this;

        this.ui.$window.on('scroll', function () {
            // End of the document reached?
            var hasMoreResultToShow = !that.ui.$searchResultFooterRegion.hasClass('hidden');
            if (that.ui.$document.height() - that.ui.$window.height() == that.ui.$window.scrollTop() && hasMoreResultToShow) {
                // $('#loading').show();

                $.ajax({
                    method: 'GET',
                    url: '/api/v1/search/strain/result/?page=' + that.scrollPage + '&size=8',
                    dataType: 'json',
                    success: function (data) {
                        that.scrollPage += 1;
                        debugger
                        // append
                    }
                });
            }
        });
    }
});
