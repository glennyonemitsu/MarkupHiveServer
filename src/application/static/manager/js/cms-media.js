CKEDITOR.plugins.add( 'cmsMedia', {
    init: function( editor ) {
        editor.addCommand( 'mediadialog',new CKEDITOR.dialogCommand( 'mydialog' ) );

        if ( editor.contextMenu ) {
            editor.addMenuGroup( 'mygroup', 10 );
            editor.addMenuItem( 'My Dialog', {
                label: 'Open dialog',
                command: 'mediadialog',
                group: 'mygroup'
            } );
            editor.contextMenu.addListener( function( element ) {
                return { 'My Dialog': CKEDITOR.TRISTATE_OFF };
            } );
            /*
            editor.ui.add( 'MyButton', CKEDITOR.UI_BUTTON, {
                label: 'My Dialog',
                command: 'mediadialog'
            });
            */
        }

        CKEDITOR.dialog.add( 'mydialog', function( api ) {
            var dialogDefinition = {
                title: 'Sample dialog',
                minWidth: 390,
                minHeight: 130,
                contents: [
                    {
                        id: 'tab1',
                        label: 'Label',
                        title: 'Title',
                        expand: true,
                        padding: 0,
                        elements: [
                            {
                                type: 'html',
                                html: '<p>This is some sample HTML content.</p>'
                            },
                            {
                                type: 'textarea',
                                id: 'textareaId',
                                rows: 4,
                                cols: 40
                            }
                        ]
                    }
                ],
                buttons: [ CKEDITOR.dialog.okButton, CKEDITOR.dialog.cancelButton ],
                onOk: function() {
                    // "this" is now a CKEDITOR.dialog object.
                    // Accessing dialog elements:
                    var textareaObj = this.getContentElement( 'tab1', 'textareaId' );
                    alert( "You have entered: " + textareaObj.getValue() );
                }
            };
            return dialogDefinition;
        } );
    }
} );
