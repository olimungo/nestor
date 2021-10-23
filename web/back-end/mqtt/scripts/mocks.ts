import { saveState } from './database';

export function mockData() {
    saveState(
        'states/shades/1',
        '{"ip": "192.168.0.177", "type": "SHADE", "state": "TOP", "tags": ["garden","city2"] }'
    );

    saveState(
        'states/shades/2',
        '{"ip": "192.168.0.122", "type": "SHADE", "state": "BOTTOM", "tags": ["entrance","city2", "door"] }'
    );

    saveState(
        'states/switches/11',
        '{"ip": "192.168.0.199", "type": "SWITCH", "state": "OFF", "tags": ["living-room","disco", "light"] }'
    );

    saveState(
        'states/clocks/10',
        '{"ip": "192.168.0.201", "type": "CLOCK", "state": "ON", "tags": ["garden","city3"] }'
    );

    saveState(
        'states/signs/1',
        '{"ip": "192.168.0.054", "type": "SIGN", "state": "ON", "tags": ["garden","city3"] }'
    );

    saveState(
        'states/signs/2',
        '{"ip": "192.168.0.055", "type": "SIGN", "state": "ON", "tags": ["garden","city4"] }'
    );
}
