'use strict';

W.ns('W.users');

W.users.ReviewsPage = Class.extend({

    ui: {
        $userId: $('.user-id')
    },

    regions: {
        $reviews: $('.user-reviews')
    },

    subTabs: {
        $strains: $('.strains-tab'),
        $dispensaries: $('.dispensaries-tab'),
        $deliveries: $('.deliveries-tab')
    },

    init: function () {
        var that = this;
        this.retrieveStrainReviews(function (reviews) {
            that.renderStrainReviews(reviews);
        });
        this.initSubTabs();
    },

    retrieveStrainReviews: function retrieveStrainReviews(success) {
        var that = this;
        $.ajax({
            method: 'GET',
            url: '/api/v1/users/{0}/reviews'.format(that.ui.$userId.val()),
            success: function (data) {
                if (data.reviews) {
                    success(data.reviews);
                }
            }
        });
    },

    retrieveDispensariesReviews: function retrieveDispensariesReviews(success) {
        success(); // TODO retrieve
    },

    retrieveDeliveriesReviews: function retrieveDeliveriesReviews(success) {
        success(); // TODO retrieve
    },

    renderStrainReviews: function renderStrainReviews(reviews) {
        var that = this;
        this.regions.$reviews.html('');
        $.each(reviews, function (index, review) {
            that.preformatReview(review);
            var template = _.template($('#user_review_template').html());
            that.regions.$reviews.append(template({'review': review}));
            that.initRating($('.overall-rating-{0}'.format(review.id)), review.strain_overall_rating);
            that.initRating($('.rating-{0}'.format(review.id)), review.rating);
            that.changeReviewText($('.review-text-{0}'.format(review.id)));
        });
        this.expandReviewText();
    },

    initRating: function initRating($ratingSelector, rating) {
        W.common.Rating.readOnly($ratingSelector, {rating: rating});
    },

    changeReviewText: function changeReviewText($review) {
        var reviewHeight = $review.height(),
            $text = $review.find('.text'),
            reviewText = $text.text(),
            fontSize = parseInt($text.css('font-size'), 10);

        if (reviewHeight / fontSize === 3) {
            reviewText = reviewText.substr(0, 150) + '... <span class="expander">Review full review</span>';
            $text.html(reviewText);
        }
    },

    expandReviewText: function expandReviewText() {
        $('.expander').on('click', function () {
            var parent = $(this).parent().parent();
            parent.find('.text').addClass('hidden');
            parent.find('.full-text').removeClass('hidden');
        });
    },

    renderDispensariesReviews: function renderDispensariesReviews(reviews) {
        this.regions.$reviews.html('ToBeDone - Dispensaries Reviews'); // TODO render
    },

    renderDeliveriesReviews: function renderDeliveriesReviews(reviews) {
        this.regions.$reviews.html('ToBeDone - Deliveries Reviews'); // TODO render
    },

    preformatReview: function preformatReview(review) {
        var date = new Date(review.created_date),
            year = date.getFullYear() - 2000,
            month = date.getMonth() + 1,
            day = date.getDate();

        review.review = review.review ? review.review : '(No review written)';
        review.created_date = '{0}/{1}/{2}'.format(month, day, year);
    },

    initSubTabs: function initSubTabs() {
        var that = this;

        this.subTabs.$strains.on('click', function () {
            $('.sub-tab').removeClass('active');
            $(this).addClass('active');
            that.retrieveStrainReviews(function (reviews) {
                that.renderStrainReviews(reviews);
            });
        });

        this.subTabs.$dispensaries.on('click', function () {
            $('.sub-tab').removeClass('active');
            $(this).addClass('active');
            that.retrieveDispensariesReviews(function (reviews) {
                that.renderDispensariesReviews(reviews);
            });
        });

        this.subTabs.$deliveries.on('click', function () {
            $('.sub-tab').removeClass('active');
            $(this).addClass('active');
            that.retrieveDeliveriesReviews(function (reviews) {
                that.renderDeliveriesReviews(reviews);
            });
        });
    }

});
