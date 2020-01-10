'use strict';

W.ns('W.pages.business');

W.pages.business.BusinessMenu = Class.extend({

    sativas: [], indicas: [], hybrids: [],

    ui: {
        $businessId: $('.business-id'),
        $locations: $('.location-select'),
        $btnStrainAdd: $('.btn-add-strain')
    },

    regions: {
        $sativas: $('.sativa-region'),
        $indicas: $('.indica-region'),
        $hybrids: $('.hybrid-region')
    },

    init: function init(options) {
        this.is_strains = options.is_strains;
        this.baseUrl = this.is_strains ?
          '/api/v1/businesses/{0}/locations/{1}/grown-strain/' : '/api/v1/businesses/{0}/locations/{1}/menu';

        this.initStrainLookupField();
        this.retrieveMenu(this.ui.$locations.val());
        this.changeLocation();
        this.addMenuItem();

        $('input[name^="price_"]').on('change', function () {
            var $input = $(this);
            $input.val(parseFloat($input.val()).toFixed(2));
        });

        $('input').on('focusin', function (e) {
            e.preventDefault();
            $('.error-message').text('');
        });
    },

    initStrainLookupField: function initStrainLookupField() {
        var lookupTemplate = _.template($('#strain-lookup-field').html());
        $('.strain-name-field').html(lookupTemplate({'lookup_placeholder': '+ Add Strain'}));
        new W.pages.strain.StrainLookup();
    },

    retrieveMenu: function retrieveMenu(locationId) {
        var that = this;
        $.ajax({
            method: 'GET',
            url: that.baseUrl.format(this.ui.$businessId.val(), locationId),
            success: function (data) {
                if (data) {
                    $.each(data, function (i, item) {
                        that.pushMenuItem(item.strain_variety, item);
                    });
                    that.renderMenus();
                }
            }
        });
    },

    renderMenus: function renderMenus() {
        this.renderMenu('SATIVAS', this.sativas, this.regions.$sativas);
        this.renderMenu('INDICAS', this.indicas, this.regions.$indicas);
        this.renderMenu('HYBRIDS', this.hybrids, this.regions.$hybrids);
    },

    renderMenu: function (menuTitle, menuItems, $menuRegion) {
        if (menuItems.length > 0) {
            var menuTemplate = _.template($('#menu-template').html());
            $menuRegion.html(menuTemplate({
                menuTitle: menuTitle,
                menuItems: menuItems,
                is_strains: this.is_strains,
                renderStrain: _.template($('#menu-item-template').html())
            }));
            $menuRegion.removeClass('hidden');
            this.changeAvailabilityInStock($menuRegion);
            this.removeMenuItem($menuRegion);
        } else {
            $menuRegion.html('');
            $menuRegion.addClass('hidden');
        }
    },

    reRenderVarietyMenu: function reRenderVarietyMenu(menuItemVariety) {
        if ('sativa' === menuItemVariety) {
            this.sativas.sort(this.sortValues);
            this.renderMenu('SATIVAS', this.sativas, this.regions.$sativas);
        }

        if ('indica' === menuItemVariety) {
            this.indicas.sort(this.sortValues);
            this.renderMenu('INDICAS', this.indicas, this.regions.$indicas);
        }

        if ('hybrid' === menuItemVariety) {
            this.hybrids.sort(this.sortValues);
            this.renderMenu('HYBRIDS', this.hybrids, this.regions.$hybrids);
        }
    },

    sortValues: function sortValues(el1, el2) {
        var aName = el1.strain_name, bName = el2.strain_name;
        return aName < bName ? -1 : aName > bName ? 1 : 0;
    },

    addMenuItem: function addMenuItem() {
        var that = this;
        this.ui.$btnStrainAdd.on('click', function (e) {
            e.preventDefault();
            var strainId = $('.lookup-input').attr('payload-id'),
                priceGram = $('input[name="price_gram"]').val(),
                priceEighth = $('input[name="price_eighth"]').val(),
                priceQuarter = $('input[name="price_quarter"]').val(),
                priceHalf = $('input[name="price_half"]').val(),
                menuItem;

            if (!strainId) {
                $('.error-message').text('Strain name is required');
                return;
            }

            if (priceGram < 0 || priceEighth < 0 || priceQuarter < 0 || priceHalf < 0) {
                $('.error-message').text('Price value cannot be negative');
                return;
            }

            menuItem = {
                strain_id: strainId,
                strain: strainId,
                price_gram: that.getPriceValue(priceGram),
                price_eighth: that.getPriceValue(priceEighth),
                price_quarter: that.getPriceValue(priceQuarter),
                price_half: that.getPriceValue(priceHalf),
                in_stock: !that.is_strains
            };

            $.ajax({
                method: 'POST',
                url: that.baseUrl.format(that.ui.$businessId.val(), that.ui.$locations.val()),
                dataType: 'json',
                data: JSON.stringify(menuItem),
                success: function (menuItem) {
                    that.clearAddMenuItemInputs();

                    if (menuItem) {
                        var variety = menuItem.strain_variety,
                            existing = that.popMenuItem(variety, menuItem.id);

                        if (existing !== null) {
                            that.deleteMenuItem(variety, menuItem.id);
                        }

                        that.pushMenuItem(variety, menuItem);
                        that.reRenderVarietyMenu(variety);
                    }
                }
            });
        });
    },

    clearAddMenuItemInputs: function clearAddMenuItemInputs() {
        $('.lookup-input').removeAttr('payload-id').removeAttr('payload-variety').val('');
        $('input[name="price_gram"]').val('');
        $('input[name="price_eighth"]').val('');
        $('input[name="price_quarter"]').val('');
        $('input[name="price_half"]').val('');
    },

    changeAvailabilityInStock: function changeAvailabilityInStock($menuRegion) {
        var that = this,
            $inStockCheckbox = $menuRegion.find('.in-stock-value');

        $inStockCheckbox.on('click', function () {
            that.processAvailability($(this));
        });
    },

    removeMenuItem: function removeMenuItem($menuRegion) {
        var that = this,
            $btnRemove = $menuRegion.find('.btn-remove-menu-item');

        $btnRemove.on('click', function () {
            var $btn = $(this),
                menuItemId = $btn.attr('id'),
                menuItemVariety = $btn.attr('variety'),
                $removeItemDialog = $('.remove-item-dialog'),
                deleteUrl;

            $removeItemDialog.find('.btn-remove').on('click', function () {
                $removeItemDialog.dialog('close');
                deleteUrl = that.is_strains ? that.baseUrl + menuItemId + '/' : that.baseUrl;

                $.ajax({
                    method: 'DELETE',
                    url: deleteUrl.format(that.ui.$businessId.val(), that.ui.$locations.val()),
                    dataType: 'json',
                    data: JSON.stringify({'menu_item_id': menuItemId}),
                    success: function () {
                        that.deleteMenuItem(menuItemVariety, menuItemId);
                        that.reRenderVarietyMenu(menuItemVariety);
                    }
                });
            });

            $removeItemDialog.find('.btn-cancel').on('click', function () {
                $removeItemDialog.dialog('close');
            });

            W.common.ConfirmDialog($removeItemDialog);
        });
    },

    processAvailability: function processAvailability($checkbox) {
        var menuItemId = $checkbox.attr('id'),
            menuItemVariety = $checkbox.attr('variety'),
            menuItem = this.popMenuItem(menuItemVariety, menuItemId);

        menuItem.in_stock = $checkbox.is(':checked');
        this.updateAvailability(menuItem);
    },

    updateAvailability: function updateAvailability(menuItem) {
        var that = this;

        $.ajax({
            method: 'PUT',
            url: this.baseUrl.format(this.ui.$businessId.val(), this.ui.$locations.val()),
            dataType: 'json',
            data: JSON.stringify({'menu_item': menuItem}),
            success: function (menuItem) {
                if (menuItem) {
                    var variety = menuItem.strain_variety,
                        existing = that.popMenuItem(variety, menuItem.id);

                    if (existing !== null) {
                        that.deleteMenuItem(variety, menuItem.id);
                    }

                    that.pushMenuItem(variety, menuItem);
                    that.reRenderVarietyMenu(variety);
                }
            }
        });
    },

    changeLocation: function changeLocation() {
        var that = this;
        this.ui.$locations.on('change', function () {
            that.sativas.length = 0;
            that.indicas.length = 0;
            that.hybrids.length = 0;

            that.regions.$sativas.html('');
            that.regions.$sativas.addClass('hidden');
            that.regions.$indicas.html('');
            that.regions.$indicas.addClass('hidden');
            that.regions.$hybrids.html('');
            that.regions.$hybrids.addClass('hidden');

            that.retrieveMenu($(this).val());
        });
    },

    pushMenuItem: function (variety, strain) {
        if ('sativa' === variety) {
            this.sativas.push(strain);
        }

        if ('indica' === variety) {
            this.indicas.push(strain);
        }

        if ('hybrid' === variety) {
            this.hybrids.push(strain);
        }
    },

    popMenuItem: function popMenuItem(variety, itemId) {
        var item = null;

        if ('sativa' === variety) {
            $.each(this.sativas, function (i, menuItem) {
                if (parseInt(itemId, 10) === menuItem.id) {
                    item = menuItem;
                }
            });
        }

        if ('indica' === variety) {
            $.each(this.indicas, function (i, menuItem) {
                if (parseInt(itemId, 10) === menuItem.id) {
                    item = menuItem;
                }
            });
        }

        if ('hybrid' === variety) {
            $.each(this.hybrids, function (i, menuItem) {
                if (parseInt(itemId, 10) === menuItem.id) {
                    item = menuItem;
                }
            });
        }

        return item;
    },

    deleteMenuItem: function deleteMenuItem(variety, itemId) {
        var menuItemId = parseInt(itemId, 10);

        if ('sativa' === variety) {
            for (var s = 0; s < this.sativas.length; s++) {
                if (this.sativas[s].id === menuItemId) {
                    this.sativas.splice(s, 1);
                    break;
                }
            }
        }

        if ('indica' === variety) {
            for (var i = 0; i < this.indicas.length; i++) {
                if (this.indicas[i].id === menuItemId) {
                    this.indicas.splice(i, 1);
                    break;
                }
            }
        }

        if ('hybrid' === variety) {
            for (var h = 0; h < this.hybrids.length; h++) {
                if (this.hybrids[h].id === menuItemId) {
                    this.hybrids.splice(h, 1);
                    break;
                }
            }
        }
    },

    getPriceValue: function getPriceValue(value) {
        return value !== '' ? value : null;
    },

    formatPriceValue: function getPriceValue(value) {
        if (value && value === '--') {
            return null;
        }

        if (value && value.toString().indexOf('$') !== -1) {
            return value.toString().substr(1, value.length);
        }

        return value ? '$' + value : '--';
    }
});
