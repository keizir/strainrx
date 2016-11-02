'use strict';

W.ns('W.pages.search.strain');

W.pages.search.strain.SearchWizardStep1 = W.pages.search.strain.SearchWizardStep.extend({

    checkedTypes: [],

    init: function init(options) {
        this._super({
            step: 1,
            model: options && options.model,
            submit_el: '.btn-step-1',
            skip_el: '.btn-skip-1',
            template_el: '#search-wizard-step1'
        });
    },

    initEventHandlers: function initEventHandlers() {
        this._super();
        this.clickTypeCheckbox();
        this.clickTypeInfo();
    },

    clickTypeCheckbox: function clickTypeCheckbox() {
        var that = this;
        $('input[type="checkbox"]').on('click', function () {
            var $checkbox = $(this);
            if ($checkbox.is(':checked')) {
                that.checkedTypes.push($checkbox.attr('name'));
            } else {
                for (var i = 0; i < that.checkedTypes.length; i++) {
                    if (that.checkedTypes[i] === $checkbox.attr('name')) {
                        that.checkedTypes.splice(i, 1);
                        break;
                    }
                }
            }

            that.toggleButtonsState();
        });
    },

    clickTypeInfo: function clickTypeInfo() {
        $('.type-info').on('click', function (e) {
            e.preventDefault();
            W.common.Dialog($('.' + $(this).parent().find('.type').attr('id') + '-dialog'));
        });
    },

    renderHTML: function renderHTML() {
        return this.$template();
    },

    submit: function submit() {
        $.publish('update_step_data', {
            step: this.step,
            data: {
                sativa: $('input[name="sativa"]').is(":checked"),
                hybrid: $('input[name="hybrid"]').is(":checked"),
                indica: $('input[name="indica"]').is(":checked")
            }
        });
        $.publish('show_step', {step: 2});
    },

    skip: function skip() {
        $.publish('update_step_data', {step: this.step, data: {skipped: true}});
        $.publish('show_step', {step: 2});
    },

    restoreState: function restoreState() {
        if (this.model.get(this.step)) {
            var step1State = this.model.get(this.step);
            if (!step1State || step1State.skipped) {
                return;
            }

            this.checkedTypes.length = 0;

            if (step1State.sativa) {
                $('input[name="sativa"]').prop('checked', 'checked');
                this.checkedTypes.push('sativa');
            }

            if (step1State.hybrid) {
                $('input[name="hybrid"]').prop('checked', 'checked');
                this.checkedTypes.push('hybrid');
            }

            if (step1State.indica) {
                $('input[name="indica"]').prop('checked', 'checked');
                this.checkedTypes.push('indica');
            }

            this.toggleButtonsState();
        }
    },

    toggleButtonsState: function toggleButtonsState() {
        var $submitBtn = $(this.submit_el),
            $skipBtn = $(this.skip_el);

        if (this.checkedTypes.length > 0) {
            $submitBtn.removeAttr('disabled');
            $skipBtn.attr('disabled', 'disabled');
        } else {
            $submitBtn.attr('disabled', 'disabled');
            $skipBtn.removeAttr('disabled');
        }
    }

});