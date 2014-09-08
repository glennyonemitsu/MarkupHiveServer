/**
 * Javascript for content entry and edit forms
 */
$(function() {
    'use strict';
    var form, title, slug, slugging, slugify, rtes;
    form = $('#content-entry');

    $('> .tabbable > ul.nav.nav-tabs > li:first-child > a', form).click();

    rtes = $('div.rte > textarea', form);

    rtes.each(function (i, rte) {
        CKEDITOR.replace(rte.name, {
            //filebrowserBrowseUrl: '/browser/browse.php',
            //filebrowserUploadUrl: '/uploader/upload.php'
        });
    });

    // tags
    $("#content_entry_tag").tagit({
        fieldName: "content_entry_tag"
    });

    // slugs
    title = $('#content_entry_title', form);
    slugging = true;
    // only dynamically creating slugs when it is a new entry
    slugify = function (text) {
        var slug;
        slug = text.toLowerCase().
            replace(/[^\w -]+/g, '').
            replace(/[ -]+/g, '-');
        if (slug.charAt(0) === '-') {
            slug = slug.substr(1);
        }
        return slug;
    };
    slug = $('#content_entry_slug', form);
    if (title.hasClass('add')) {
        slug.on('keydown', function () {
            slugging = false;
        });
        title.on('keyup', function () {
            if (slugging) {
                slug.val(slugify(title.val()));
            }
        });
    }

    // enforce slug format
    slug.on('keydown', function () {
        slug.val(slugify(slug.val()));
    });
    slug.on('blur', function () {
        slug.val(slug.val().replace(/[- ]+$/, ''))
    });
    title.on('blur', function () {
        slug.val(slug.val().replace(/[- ]+$/, ''))
    });
});
