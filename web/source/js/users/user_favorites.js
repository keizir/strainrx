'use strict';

W.ns('W.users');

W.users.FavoritesPage = Class.extend({

    ui: {
        $userId: $('.user-id')
    },

    regions: {
        $favorites: $('.user-favorites')
    },

    subTabs: {
        $strains: $('.strains-tab'),
        $dispensaries: $('.dispensaries-tab'),
        $deliveries: $('.deliveries-tab')
    },

    init: function () {
        var that = this;
        this.retrieveStrainFavorites(function (favorites) {
            that.renderStrainFavorites(favorites);
            that.removeStrainFavorite();
        });
        this.initSubTabs();
    },

    retrieveStrainFavorites: function retrieveStrainFavorites(success) {
        var that = this;
        $.ajax({
            method: 'GET',
            url: '/api/v1/users/{0}/favorites/strain'.format(that.ui.$userId.val()),
            success: function (data) {
                if (data.favorites) {
                    success(data.favorites);
                }
            }
        });
    },

    retrieveDispensariesFavorites: function retrieveDispensariesFavorites(success) {
        success(); // TODO retrieve
    },

    retrieveDeliveriesFavorites: function retrieveDeliveriesFavorites(success) {
        success(); // TODO retrieve
    },

    renderStrainFavorites: function renderStrainFavorites(favorites) {
        var that = this,
            template = _.template($('#user_favorite_strain_template').html());

        this.regions.$favorites.html('');

        if (favorites && favorites.length === 0) {
            this.regions.$favorites.html('No favorite strains');
        }

        $.each(favorites, function (index, favorite) {
            that.preformatFavorite(favorite);
            that.regions.$favorites.append(template({'favorite': favorite}));
            that.initRating($('.overall-rating-{0}'.format(favorite.id)), favorite.strain_overall_rating);
        });
    },

    initRating: function initRating($ratingSelector, rating) {
        if (rating !== 'Not Rated') {
            W.common.Rating.readOnly($ratingSelector, {rating: rating});
        }
    },

    removeStrainFavorite: function removeStrainFavorite() {
        var that = this;
        $('.removable').on('click', function () {
            $.ajax({
                method: 'DELETE',
                url: '/api/v1/users/{0}/favorites/strain/{1}'.format(that.ui.$userId.val(), $(this).prop('id')),
                success: function () {
                    window.location.reload();
                }
            });
        });
    },

    renderDispensariesFavorites: function renderDispensariesFavorites(favorites) {
        this.regions.$favorites.html('No Dispensaries Added'); // TODO render
    },

    renderDeliveriesFavorites: function renderDeliveriesFavorites(favorites) {
        this.regions.$favorites.html('No Deliveries Added'); // TODO render
    },

    preformatFavorite: function preformatFavorite(review) {
        var date = new Date(review.created_date),
            year = date.getFullYear() - 2000,
            month = date.getMonth() + 1,
            day = date.getDate();

        review.created_date = '{0}/{1}/{2}'.format(month, day, year);
    },

    initSubTabs: function initSubTabs() {
        var that = this;

        this.subTabs.$strains.on('click', function () {
            $('.sub-tab').removeClass('active');
            $(this).addClass('active');
            that.retrieveStrainFavorites(function (favorites) {
                that.renderStrainFavorites(favorites);
            });
        });

        this.subTabs.$dispensaries.on('click', function () {
            $('.sub-tab').removeClass('active');
            $(this).addClass('active');
            that.retrieveDispensariesFavorites(function (favorites) {
                that.renderDispensariesFavorites(favorites);
            });
        });

        this.subTabs.$deliveries.on('click', function () {
            $('.sub-tab').removeClass('active');
            $(this).addClass('active');
            that.retrieveDeliveriesFavorites(function (favorites) {
                that.renderDeliveriesFavorites(favorites);
            });
        });
    }

});
