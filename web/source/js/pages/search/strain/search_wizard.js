'use strict';

W.ns('W.pages.search.strain');

W.pages.search.strain.SearchWizard = W.common.Wizard.extend({

    mixpanelEventName: 'strain_search',

    steps: {},

    ui: {
        $currentUserId: $('.current-user-id')
    },

    init: function init(options) {
        this._super({
            model: options && options.model
        });

        this.name = 'SearchWizard';
        this.refreshSearchSettingAndRenderStep({step: 1});

        W.subscribe.apply(this);
    },

    _on_show_step: function _on_show_step(ev, data) {
        this.renderStepContent(data.step);
    },

    _on_show_refreshed_step: function _on_show_refreshed_step(ev, data) {
        this.refreshSearchSettingAndRenderStep({step: data.step});
    },

    _on_update_step_data: function _on_update_step_data(ev, data) {
        this.updateData(data);
    },

    _on_submit_form: function _on_submit_form(ev, data) {
        var that = this,
            search_criteria_json = {search_criteria: {step1: data[1], step2: data[2], step3: data[3], step4: data[4]}},
            search_criteria = JSON.stringify(search_criteria_json);

        $.ajax({
            method: 'POST',
            url: '/api/v1/users/{0}/searches'.format(that.getCurrentUserId()),
            dataType: 'json',
            data: search_criteria
        });

        $.ajax({
            method: 'POST',
            url: '/api/v1/search/strain',
            dataType: 'json',
            data: search_criteria,
            success: function () {
                window.location.href = '/search/strain/results/';
            },
            error: function (e) {
                if (400 === e.status) {
                    W.common.VerifyEmailDialog();
                }
            }
        });

        W.users.UserSettings.update(that.getCurrentUserId(), W.users.UserSettings.settingName_SearchFilter, {'searchFilter': 'all'});
        W.common.Mixpanel.track(this.mixpanelEventName, that.getMixpanelData(data));
    },

    getMixpanelData: function getMixpanelData(data) {
        var result = {};

        if (data[1] && !data[1].skipped) {
            $.each(data[1], function (key, value) {
                result[key] = value;
            })
        }

        if (data[2] && !data[2].skipped) {
            $.each(data[2].effects, function (i, effect) {
                result[effect.name] = effect.value;
            })
        }

        if (data[3] && !data[3].skipped) {
            $.each(data[3].effects, function (i, effect) {
                result[effect.name] = effect.value;
            });
        }

        if (data[4] && !data[4].skipped) {
            $.each(data[4].effects, function (i, effect) {
                result[effect.name] = effect.value;
            });
        }

        return result;
    },

    getCurrentUserId: function getCurrentUserId() {
        return this.ui.$currentUserId.val();
    },

    initSteps: function initSteps() {
        var that = this,
            stepData = {model: this.model, currentUserId: this.getCurrentUserId()};

        this.steps[1] = new W.pages.search.strain.SearchWizardStep1(stepData);
        this.steps[2] = new W.pages.search.strain.SearchWizardStep2(stepData);
        this.steps[3] = new W.pages.search.strain.SearchWizardStep3(stepData);
        this.steps[4] = new W.pages.search.strain.SearchWizardStep4(stepData);

        $(window).hashchange(function () {
            that.refreshSearchSettingAndRenderStep({step: parseInt(location.hash.split('#')[1], 10)});
        });
    },

    clickStep: function clickStep() {
        $('.wizard-step').on('click', function () {
            $.publish('show_refreshed_step', {step: parseInt($(this).text(), 10)});
        });
    },

    handleStepClick: function handleStepClick(step) {
        var $step = $('.wizard-step');
        $.each($step, function () {
            var $s = $(this),
                stepNumber = parseInt($s.text(), 10);

            if (stepNumber < step) {
                $s.addClass('passed').removeClass('active disabled');
            }

            if (stepNumber === step) {
                $s.addClass('active').removeClass('passed disabled');
            }

            if (stepNumber > step) {
                $s.addClass('disabled').removeClass('active passed');
            }
        });
    },

    refreshSearchSettingAndRenderStep: function refreshSearchSettingAndRenderStep(data) {
        var that = this;
        W.users.UserSettings.get(this.getCurrentUserId(), W.users.UserSettings.settingName_WizardSearch, function (setting) {
            that.model.setData(setting);
            that.renderStepContent(data.step);
        });
    },

    renderStepContent: function renderStepContent(step) {
        window.location.hash = step;
        this.handleStepClick(step);
        this.prepareContentAndShow(step);
    },

    prepareContentAndShow: function prepareContentAndShow(step) {
        var that = this,
            stepView = this.steps[step];

        switch (step) {
            case 1:
                this.showStep(stepView);
                break;

            case 2:
                that.getEffects('effect', function (data) {
                    stepView.renderData = {effects: data};
                    that.showStep(stepView);
                });
                break;

            case 3:
                that.getEffects('benefit', function (data) {
                    stepView.renderData = {benefits: data};
                    that.showStep(stepView);
                });
                break;

            case 4:
                that.getEffects('side_effect', function (data) {
                    stepView.renderData = {side_effects: data};
                    that.showStep(stepView);
                });
                break;

            default:
                throw new Error('Invalid step number: {0}.'.format(step));
        }
    },

    getEffects: function getEffects(type, callback) {
        $.ajax({
            method: 'GET',
            url: '/api/v1/search/effect/{0}'.format(type),
            success: function (data) {
                callback(data);
            }
        });
    },

    showStep: function showStep(stepView) {
        this.destroy();
        this.show(stepView);
        stepView.restoreState();
    },

    updateData: function updateData(data) {
        this.model.set(data.step, data.data);
        W.users.UserSettings.update(this.getCurrentUserId(), W.users.UserSettings.settingName_WizardSearch, this.model.getData());
    }

});
