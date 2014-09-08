/**
 * Javascript to dynamically update the content type meta data
 * and edit form
 */

$(function() {
    'use strict';

        
        // content type meta data
    var modal_type_meta,
        modal_type_create,
        modal_type_delete,

        // field groups
        field_groups,
        field_groups_nav,
        field_groups_nav_width,
        field_groups_content,
        field_groups_nav_refresh,
        modal_group_add,
        modal_group_edit,
        modal_group_delete,
        partial_group_header,
        partial_group_toolbar,

        // field type
        partial_field,

        // universal
        api_handler,
        form, // general parent form
        uuid;

    form = $('form#content-type');
    uuid = $('input[name="type-uuid"]').val();

    /**
     * default api response handler wrapper. if there are any errors or 
     * notices then it will show on the page and the wrapped function will not
     * be called.
     */
    api_handler = function (fn) {
        var wrapper;
        wrapper = function (res) {
            var i, errors, notices;
            if (res.success) {
                fn(res);
            } else {
                if (res.success === false) {
                    if (res.error) {
                        errors = $('<div class="alert alert-block alert-error" />');
                        errors.append('<button type="button" class="close" data-dismiss="alert">&times;</button>');
                        errors.append('<h4>Error</h4>');
                        for (i in res.error) {
                            errors.append('<p>' + res.error[i] + '</p>');
                        }
                        form.prepend(errors);
                    }
                    if (res.notice) {
                        notices = $('<div class="alert alert-block" />');
                        notices.append('<button type="button" class="close" data-dismiss="alert">&times;</button>');
                        notices.append('<h4>Warning</h4>');
                        for (i in res.notice) {
                            notices.append('<p>' + res.notice[i] + '</p>');
                        }
                        form.prepend(notices);
                    }
                }
            }
        };
        return wrapper;
    };

    /**
     * content type name or description changes
     */
    modal_type_meta = $('#modal-type-meta-edit');
    modal_type_meta.on('show', function () {
        var name, description;
        name = $('#type-name').text();
        description = $('#type-description').text();

        $('input[name="type-name"]', modal_type_meta).val(name);
        $('input[name="type-description"]', modal_type_meta).val(description);

    });
    modal_type_meta.on('shown', function () {
        $('input[name="type-name"]', modal_type_meta).focus();
    });
    $('form', modal_type_meta).submit(function() {
        var data, uri;

        uri = '/cms/content-type/' + uuid + '/';
        data = {
            action: 'update',
            name: $('input[name="type-name"]', modal_type_meta).val(),
            description: $('input[name="type-description"]', modal_type_meta).val()
        };

        $.post(uri, data, api_handler(function (res) {
            $('#type-name').text(res.name);
            $('#type-description').text(res.description);
        }), 'json');
        modal_type_meta.modal('hide');
        return false;
    });

    /**
     * content type delete
     */
    modal_type_delete = $('#modal-type-delete');
    modal_type_delete.submit(function () {
        var uri, data;

        uri = '/cms/content-type/' + uuid + '/';
        data = {
            action: 'delete',
            confirm_phrase: $('input[name="confirm-phrase"]', modal_type_delete).val()
        };

        $.post(uri, data, api_handler(function (res) {
            location.pathname = '/cms/content-types/';
        }), 'json');
        modal_type_delete.modal('hide');
        return false;
    });


    /**
     * adding field groups
     */
    partial_group_toolbar = $('#partial-field-group-toolbar > div');
    field_groups = $('#field-groups');
    field_groups_nav = $('> #field-groups-nav > ul.nav', field_groups);
    field_groups_content = $('> div.tab-content', field_groups);
    field_groups_nav_width = function () {
        var width;
        width = 0;
        $('> li', field_groups_nav).each(function (i, item) {
            width += $(item).outerWidth(true);
        });
        return width;
    };
    // check if nav needs sliding controls
    field_groups_nav_refresh = function () {
        var width;
        width = field_groups_nav_width();
        if (width >= field_groups.outerWidth()) {
            $('.control', field_groups).show();
            field_groups_nav
                .width(width)
                .addClass('scroll');
        } else {
            $('.control', field_groups).hide();
            field_groups_nav
                .width(field_groups.outerWidth())
                .removeClass('scroll');
        }
    };
    field_groups_nav_refresh();
    // sliding controls functionality
    $('.control', field_groups).click(function () {
        var left_margin, 
            window_length,
            move_length, 
            nav_length, 
            max_length, 
            space_remaining;

        max_length = 250; // max pixels to move per click
        field_groups_nav_refresh(); // need recalculating for first click due to loading fonts
        left_margin = parseInt(field_groups_nav.css('marginLeft'), 10);

        switch (this.id) {
            case 'field-groups-nav-left':
                space_remaining = left_margin;
                move_length = Math.min(left_margin + max_length, 0);
                field_groups_nav.css('marginLeft', move_length + 'px');
            break;
            case 'field-groups-nav-right':
                window_length = field_groups.outerWidth();
                nav_length = field_groups_nav_width() + 60; // 60 = width of controls
                space_remaining = nav_length - window_length + left_margin; // adding neg margin
                move_length = -Math.min(space_remaining, max_length) + left_margin;
                field_groups_nav.css('marginLeft', move_length + 'px');
            break;
        }
    });

    // adding modal form
    modal_group_add = $('#modal-field-group-add');
    modal_group_add.on('show', function () {
        $('input[name="field-group-name"]', modal_group_add).val('');
    });
    modal_group_add.on('shown', function () {
        $('input[name="field-group-name"]', modal_group_add).focus();
    });
    $('form', modal_group_add).submit(function () {
        var uri, data;

        uri = '/cms/field-group/';
        data = {
            content_type_uuid: uuid,
            name: $('input[name="field-group-name"]', modal_group_add).val()
        };

        $.post(uri, data, api_handler(function (res) {
            var tab, pane;

            tab = $('<li><a data-toggle="tab" href="#' + res.uuid + '">' + res.name + '</a></li>');
            pane = $('<div id="' + res.uuid + '" class="tab-pane" />');
            pane.append(partial_group_toolbar.clone(true).show());
            pane.data('name', res.name);
            pane.data('uuid', res.uuid);
            
            field_groups_nav.append(tab);
            field_groups_content.append(pane);
            field_groups_nav_refresh();
        }), 'json');
        modal_group_add.modal('hide');
        return false;
    });

    /**
     * all field group edit buttons now and new ones in the future must
     * prepopulate the modal form
     */
    modal_group_edit = $('#modal-field-group-edit');
    modal_group_edit.on('shown', function () {
        $('input[name="field-group-name"]', modal_group_edit).focus();
    });
    field_groups.on('click', '.modal-field-group-edit', function () {
        var panel, uuid, name;
        panel = $(this).parents('div.tab-pane');
        uuid = panel.data('uuid');
        name = panel.data('name');
        $('input[name="field-group-name"]', modal_group_edit).val(name);
        $('input[name="field-group-uuid"]', modal_group_edit).val(uuid);
    });
    $('form', modal_group_edit).submit(function () {
        var uri, data, name, fg_uuid;

        name = $('input[name="field-group-name"]', this).val();
        fg_uuid = $('input[name="field-group-uuid"]', this).val();

        uri = '/cms/field-group/' + fg_uuid + '/';
        data = {
            action: 'update',
            content_type_uuid: uuid,
            name: name,
            fg_uuid: fg_uuid
        };

        $.post(uri, data, api_handler(function (res) {
            console.log(res);
            var panel, nav_tab, fg;
            fg = res.field_group;
            panel = $('#' + fg.uuid);
            panel.data('name', fg.name);
            nav_tab = $('a[href="#' + fg.uuid + '"]');
            nav_tab.text(fg.name);

        }), 'json');

        modal_group_edit.modal('hide');
        return false;
    });
    
    /**
     * field group removals and modal form prepopulation
     */
    modal_group_delete = $('#modal-field-group-delete');
    field_groups.on('click', '.modal-field-group-delete', function () {
        var panel, uuid, name;
        panel = $(this).parents('div.tab-pane');
        uuid = panel.data('uuid');
        $('input[name="field-group-uuid"]', modal_group_delete).val(uuid);
    });
    $('form', modal_group_delete).submit(function () {
        var uri, data, name, fg_uuid;

        fg_uuid = $('input[name="field-group-uuid"]', this).val();

        uri = '/cms/field-group/' + fg_uuid + '/';
        data = {
            action: 'delete',
            content_type_uuid: uuid,
            fg_uuid: fg_uuid
        };

        $.post(uri, data, api_handler(function (res) {
            var group, fg_uuid, nav_tab, panel;
            group = res.field_group;
            fg_uuid = group.uuid;
            nav_tab = $('a[href="#' + fg_uuid + '"]', field_groups).parent();
            panel = $('#' + fg_uuid);

            nav_tab.remove();
            panel.remove();
            return;
        }), 'json');

        modal_group_delete.modal('hide');
        return false;
    });

    /**
     * field group shift left and right
     */
    field_groups.on('click', 'button.modal-field-group-shift', function () {
        var uri, data, panel, fg_uuid, direction;
        panel = $(this).parents('div.tab-pane');
        fg_uuid = panel.data('uuid');
        direction = $(this).data('direction');

        uri = '/cms/field-group/' + fg_uuid + '/';
        data = {
            action: 'shift-' + direction,
            content_type_uuid: uuid,
            fg_uuid: fg_uuid
        };

        $.post(uri, data, api_handler(function (res) {
            var groups, nav_item, prev, next;
            nav_item = $('a[href="#' + fg_uuid + '"]', field_groups).parent();
            switch (direction) {
                case 'left':
                    prev = nav_item.prev();
                    if (prev.length) {
                        prev.before(nav_item);
                    }
                break;
                case 'right':
                    next = nav_item.next();
                    if (next.length) {
                        next.after(nav_item);
                    }
                break;
            }
            return;
        }), 'json');
        return false;
    });

    partial_field = $('#partial-field > .field');
    field_groups.on('click', 'button.add-field', function () {
        var uri, data, fg_uuid, panel, fields;
        panel = $(this).parents('div.tab-pane');
        fg_uuid = panel.data('uuid');

        uri = '/cms/field-group/' + fg_uuid + '/';
        data = {
            action: 'create-field',
            content_type_uuid: uuid,
            fg_uuid: fg_uuid
        };

        $.post(uri, data, api_handler(function (res) {
            var field;
            field = partial_field.clone(true);
            field.attr('id', res.uuid);
            $('input[name="name"]', field).val(res.name);
            fields = $('div.fields', panel);
            fields.append(field);
        }), 'json');

        return false;
    });
    field_groups.on('change', '.field :input', function () {
        var uri, data, fuuid, field;
        field = $(this).parents('div.field');
        fuuid = field.attr('id');

        uri = '/cms/field/' + fuuid  + '/';
        data = {
            action: 'update',
            content_type_uuid: uuid,
            type_key: $('select[name="type_key"]', field).val(),
            name: $('input[name="name"]', field).val()
        };

        $.post(uri, data, api_handler(function (res) {
        }), 'json');
    });
    field_groups.on('click', '.field button.meta', function () {
        var uri, data, button, fuuid, field, action;
        button = $(this);
        field = button.parents('div.field');
        fuuid = field.attr('id');
        if (button.hasClass('delete')) {
            action = 'delete';
        } else if (button.hasClass('shift-up')) {
            action = 'shift-up';
        } else if (button.hasClass('shift-down')) {
            action = 'shift-down';
        } else {
            return false;
        }

        uri = '/cms/field/' + fuuid  + '/';
        data = {
            action: action,
            content_type_uuid: uuid,
        };
        $.post(uri, data, api_handler(function (res) {
            var prev, next;
            switch (action) {
                case 'delete':
                    field.remove();
                break;
                case 'shift-up':
                    prev = field.prev();
                    if (prev.length) {
                        prev.before(field);
                    }
                break;
                case 'shift-down':
                    next = field.next();
                    if (next.length) {
                        next.after(field);
                    }
                break;
            }
        }), 'json');
        return false;
    });

    $('> li:first', field_groups_nav).addClass('active');
    $('> div:first', field_groups_content).addClass('active');
    
});
