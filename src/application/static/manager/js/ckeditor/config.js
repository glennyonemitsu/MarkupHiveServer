CKEDITOR.editorConfig = function( config ) {
    config.extraPlugins = 'image';
    config.toolbar = [
        {   name: 'basicstyles', 
            groups: [ 'basicstyles', 'cleanup' ], 
            items: [ 'Bold', 'Italic', 'Strike', '-', 'RemoveFormat' ] },
        {   name: 'paragraph', 
            groups: [ 'list', 'indent', 'blocks', 'align', 'bidi' ], 
            items: [ 'NumberedList', 'BulletedList', 'Blockquote' ] },
        {   name: 'links', 
            items: [ 'Link', 'Unlink' ] },
        //{   name: 'insert', items: [ 'Image' ] },
        {   name: 'document', 
            groups: [ 'mode', 'document', 'doctools' ], 
            items: [ 'Source', '-', 'Maximize' ] },
        {   name: 'styles', 
            items: [ 'Styles', 'Format', 'FontSize', 'TextColor' ] },
    ];
};
