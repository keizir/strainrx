'use strict';

W.ns('W.pages.business');

W.pages.business.BusinessLocations = Class.extend({

    errors: {},

    locations: {},

    ui: {
        $businessId: $('.business-id'),
        $btnAddLocation: $('.btn-add-location'),
        $btnUpdateLocations: $('.btn-update-locations')
    },

    regions: {
        $locations: $('.locations-group')
    },

    templates: {
        $location: _.template($('#business_location').html())
    },

    init: function init() {
        var that = this;

        this.retrieveLocations(function (locations) {
            $.each(locations, function (i, location) {
                that.locations[location.id] = location;
                that.regions.$locations.append(that.templates.$location({'l': location}));
                that.prepareAndShowDeliveryDistanceSlider(location.id, location.delivery);
            });

            that.registerAllInputEvents($('input'));
            that.clickAddLocation();
            that.clickUpdateLocations();
            that.clickRemoveLocation($('.btn-trash'));
        });
    },

    retrieveLocations: function retrieveLocations(successCallback) {
        $.ajax({
            method: 'GET',
            url: '/api/v1/businesses/{0}/locations/0'.format(this.ui.$businessId.val()),
            success: function (data) {
                successCallback(data.locations);
            }
        });
    },

    registerAllInputEvents: function registerAllInputEvents($input) {
        var that = this;

        $input.on('focusout', function () {
            that.updateLocationInputFields($(this));
        });

        $input.on('change', function () {
            that.updateLocationCheckboxFields($(this));
            that.ui.$btnAddLocation.addClass('hidden');
            that.ui.$btnUpdateLocations.removeClass('hidden');
        });
    },

    updateLocationInputFields: function updateLocationInputFields($input) {
        if ($input.prop('type') === 'text' || $input.prop('type') === 'number') {
            var that = this,
                inputValue = $input.val(),
                inputName = $input.prop('name'),
                inputNameParts = inputName.split('__'),
                fieldName = inputNameParts[0],
                locationId = inputNameParts[1],
                messageRegion = $('.error-message-{0}'.format(inputNameParts[1]));

            if (!inputValue || inputValue.trim().length === 0) {
                var $label = $('label[for="{0}"]'.format(inputName)),
                    message = '{0} is required'.format($label.text());

                that.addError(locationId, inputName, message);
                messageRegion.text(message);
                return;
            }

            messageRegion.text('');
            $('.common-error-messages').text('');

            $.each(this.locations, function (index) {
                if (index === locationId.toString()) {
                    that.cleanError(locationId, inputName);

                    if (fieldName === 'location_name') {
                        that.locations[index].location_name = inputValue;
                        return;
                    }

                    if (fieldName === 'street_address') {
                        that.locations[index].street1 = inputValue;
                        return;
                    }

                    if (fieldName === 'city') {
                        that.locations[index].city = inputValue;
                        return;
                    }

                    if (fieldName === 'state') {
                        that.locations[index].state = inputValue;
                        return;
                    }

                    if (fieldName === 'zip_code') {
                        that.locations[index].zip_code = inputValue;
                    }
                }
            });
        }
    },

    updateLocationCheckboxFields: function updateLocationCheckboxFields($input) {
        if ($input.prop('type') === 'checkbox') {
            var that = this,
                inputName = $input.prop('name'),
                inputNameParts = inputName.split('__'),
                fieldName = inputNameParts[0],
                locationId = inputNameParts[1],
                messageRegion = $('.error-message-{0}'.format(inputNameParts[1]));

            $('.common-error-messages').text('');
            messageRegion.text('');

            $.each(this.locations, function (index) {
                if (index === locationId.toString()) {
                    that.cleanError(locationId, 'delivery__{0}'.format(locationId));
                    that.cleanError(locationId, 'dispensary__{0}'.format(locationId));

                    if (fieldName === 'dispensary') {
                        that.locations[index].dispensary = $input.is(':checked');
                    }

                    if (fieldName === 'delivery') {
                        that.locations[index].delivery = $input.is(':checked');
                        that.prepareAndShowDeliveryDistanceSlider(locationId, that.locations[index].delivery);
                    }

                    if (!that.locations[index].dispensary && !that.locations[index].delivery) {
                        messageRegion.text('Business type is required');
                        that.addError(locationId, inputName, 'Business type is required');
                    }
                }
            });
        }
    },

    prepareAndShowDeliveryDistanceSlider: function prepareAndShowDeliveryDistanceSlider(locationId, isDelivery) {
        var $sliderArea = $('.slider-area-{0}'.format(locationId));
        if (isDelivery) {
            $sliderArea.removeClass('hidden');
            this.showDeliveryDistanceSlider($sliderArea, locationId);
        } else {
            $sliderArea.addClass('hidden');
        }
    },

    showDeliveryDistanceSlider: function showDeliveryDistanceSlider($sliderArea, locationId) {
        var that = this,
            $sliderValue = $sliderArea.find('.slider-value'),
            $slider = $sliderArea.find('.slider-{0}'.format(locationId));
        $slider.slider({
            range: 'min',
            value: that.locations[locationId].delivery_radius ? that.locations[locationId].delivery_radius : 5,
            min: 5, max: 50, step: 0.5,
            slide: function (event, ui) {
                $sliderValue.text('{0} Miles'.format(ui.value));
                that.locations[locationId].delivery_radius = ui.value;
                that.ui.$btnAddLocation.addClass('hidden');
                that.ui.$btnUpdateLocations.removeClass('hidden');
            }
        });
        $sliderValue.text('{0} Miles'.format($slider.slider('value')));
    },

    clickAddLocation: function clickAddLocation() {
        var that = this;

        this.ui.$btnAddLocation.on('click', function (e) {
            e.preventDefault();
            that.ui.$btnAddLocation.addClass('hidden');
            that.ui.$btnUpdateLocations.removeClass('hidden');

            var locationClientId = 'tmpId{0}'.format(new Date().getTime());
            that.locations[locationClientId] = {
                location_name: null, manager_name: null, location_email: null,
                phone: null, ext: null,
                dispensary: false, delivery: false, delivery_radius: null,
                mon_open: null, mon_close: null,
                tue_open: null, tue_close: null,
                wed_open: null, wed_close: null,
                thu_open: null, thu_close: null,
                fri_open: null, fri_close: null,
                sat_open: null, sat_close: null,
                sun_open: null, sun_close: null
            };
            that.regions.$locations.append(that.templates.$location({'l': {'id': locationClientId}}));
            that.registerAllInputEvents($('.location-{0}'.format(locationClientId)).find('input'));
            that.clickRemoveLocation($('.btn-trash-{0}'.format(locationClientId)));
            that.addError(locationClientId, 'delivery__{0}'.format(locationClientId), 'Business type is required');
        });
    },

    clickUpdateLocations: function clickUpdateLocations() {
        var that = this;

        this.ui.$btnUpdateLocations.on('click', function (e) {
            e.preventDefault();

            $.each($('input[type="text"], input[type="number"]'), function (i, $input) {
                var v = $input.value;
                if (!v || v.trim().length === 0) {
                    var inputName = $input.name,
                        $label = $('label[for="{0}"]'.format(inputName)),
                        inputNameParts = inputName.split('__'),
                        locationId = inputNameParts[1],
                        message = '{0} is required'.format($label.text());

                    that.addError(locationId, inputName, message);
                }
            });

            if (that.hasErrors()) {
                $.each(that.errors, function (locationId, locationErrors) {
                    var locationError = '';

                    $.each(locationErrors, function (index, error) {
                        locationError += '<p>' + error.message + '</p>';
                    });

                    $('.error-message-{0}'.format(locationId)).html(locationError);
                    $('.common-error-messages').text('Some locations have errors');
                });
                return;
            }

            var locationsToSend = [];
            $.each(that.locations, function (locationId, location) {
                locationsToSend.push(location);
            });

            $.ajax({
                method: 'PUT',
                url: '/api/v1/businesses/{0}/locations/0'.format(that.ui.$businessId.val()),
                dataType: 'json',
                data: JSON.stringify({'locations': locationsToSend}),
                success: function () {
                    that.ui.$btnAddLocation.removeClass('hidden');
                    that.ui.$btnUpdateLocations.addClass('hidden');
                    that.showSuccessMessage('Locations were updated');
                    window.location.reload();
                },
                error: function (error) {
                    if (error.status === 400) {
                        var errorJson = W.common.Parser.parseJson(error.responseText);
                        $('.common-error-messages').text(errorJson.error);
                    }
                }
            });
        });
    },

    clickRemoveLocation: function clickRemoveLocation($btnTrash) {
        var that = this;

        $btnTrash.on('click', function () {
            var locationId = $(this).prop('id');
            if (locationId.startsWith('tmpId')) {
                delete that.locations[locationId];
                delete that.errors[locationId];
                $('.location-{0}'.format(locationId)).html('');
                return;
            }

            var $removeLocationDialog = $('.remove-location-dialog');

            $removeLocationDialog.find('.btn-remove').on('click', function () {
                $removeLocationDialog.dialog('close');
                $.ajax({
                    method: 'DELETE',
                    url: '/api/v1/businesses/{0}/locations/{1}'.format(that.ui.$businessId.val(), locationId),
                    success: function () {
                        that.showSuccessMessage('Location was removed');
                        window.location.reload();
                    }
                });
            });

            $removeLocationDialog.find('.btn-cancel').on('click', function () {
                $removeLocationDialog.dialog('close');
            });

            W.common.ConfirmDialog($removeLocationDialog);
        });
    },

    showSuccessMessage: function showSuccessMessage(message) {
        var $commonError = $('.common-error-messages');
        $commonError.text(message);
        $commonError.removeClass('error-message').addClass('success-message');
        setTimeout(function () {
            $commonError.text('');
            $commonError.addClass('error-message').removeClass('success-message');
        }, 2000);
    },

    hasErrors: function hasErrors() {
        return !_.isEmpty(this.errors);
    },

    addError: function addError(locationId, inputName, message) {
        if (!this.errors[locationId]) {
            this.errors[locationId] = [];
        }

        if (this.errors[locationId].length === 0) {
            this.errors[locationId].push({field: inputName, message: message});
        } else {
            var filtered = _.filter(this.errors[locationId], function (e) {
                return e.field === inputName;
            });

            if (filtered.length === 0) {
                this.errors[locationId].push({field: inputName, message: message});
            }
        }
    },

    cleanError: function cleanError(locationId, inputName) {
        if (this.errors[locationId]) {
            for (var i = 0; i < this.errors[locationId].length; i++) {
                if (this.errors[locationId][i].field === inputName) {
                    this.errors[locationId].splice(i, 1);
                    break;
                }
            }

            if (this.errors[locationId].length === 0) {
                delete this.errors[locationId];
            }
        }
    }

});
