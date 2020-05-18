/*
Use this class when you want to perform different actions depending on a global mode.
For example:

let strokeManager = new ModeManager;

strokeManager.registerMode( "paint-construction-lines", {
    // Optional:
    'enterMode': function() { code that runs when someone switches to this mode. }
    'exitMode': function() { code that runs when someone switches to this mode. },
    
    'strokeStart': function( any parameters you want ) { code that runs when a stroke starts },
    'strokeEnd': function( any parameters you want ) { code that runs when a stroke ends }
    } );

strokeManager.registerMode( "paint-descriptive-lines", {
    // Optional:
    'enterMode': function() { code that runs when someone switches to this mode. }
    'exitMode': function() { code that runs when someone switches to this mode. },
    
    'strokeStart': function( any parameters you want ) { code that runs when a stroke starts },
    'strokeEnd': function( any parameters you want ) { code that runs when a stroke ends }
    } );

// When the user switches tools:
strokeManager.switchToMode( "paint-descriptive-lines" );

// When you determine from the UI that a stroke is starting:
strokeManager.strokeStart( arguments );

// When you determine from the UI that a stroke is ending:
strokeManager.strokeEnd( arguments );
*/


class ModeManager {
    
    constructor() {
        this._registry = {};
        this._currentMode = undefined;
    }

    registerMode( name, mode ) {
        this._registry[ name ] = mode;
    }

    switchToMode( name ) {
        if( this._currentMode !== undefined && this._currentMode.exitMode !== undefined ) {
            this._currentMode.exitMode();
        }

        this._currentMode = this._registry[name];
        if( this._currentMode !== undefined && this._currentMode.enterMode !== undefined ) {
            this._currentMode.enterMode();
        }
    }

    get currentMode() {
        return this._currentMode;
    }
}

export{ ModeManager }
