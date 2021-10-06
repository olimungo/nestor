import { useEffect, useRef, useState } from 'react';
import { io } from 'socket.io-client';
import { AppContext, DevicesByTagsType, IotDevice } from '@models';
import { AppFooter, AppHeader } from '@components';
import { Redirect, Route, Switch, useHistory } from 'react-router';
import { Commands, Devices, Tags } from '@pages';

function App() {
    const history = useHistory();
    const init = useRef(true);
    const [devices, setDevices] = useState<IotDevice[]>([]);
    const [selectedDevices, setSelectedDevices] = useState<DevicesByTagsType>();
    
    useEffect(() => {
        console.log('SOCKET init');

        const socket = io(
            process.env.REACT_APP_WEBSOCKETS || 'ws://localhost:3001'
        );
        
        function devicesReceived(devices: IotDevice[]) {
            setDevices(devices);
        };

        function updateDevice(device:IotDevice) {
            console.log('update', device);
            setDevices((devices) => [...devices, device]);
        };

        function removeDevice(deviceToRemoveId: string) {
            console.log('remove', deviceToRemoveId);
            setDevices((devices) => devices.filter(device => device.id !== deviceToRemoveId));
        };

        socket.on('devices', devicesReceived);
        
        socket.on('update-device', updateDevice);
        
        socket.on('remove-device', removeDevice);
        
        socket.emit('get-devices');

        return () => {
            console.log('SOCKET off');
            socket.off('devices', devicesReceived);
            socket.off('update-device', updateDevice);
            socket.off('remove-device', removeDevice);
        };
    }, []);

    const handleControl = (selectedDevices: DevicesByTagsType) => {
        setSelectedDevices(selectedDevices);
        history.push('/control');
    };

    const handleCommand = (device: string, command: string) => {
        console.log('handleCommand', device, command);
        
        // socket.emit('mqtt-command', { device, command });
    };

    return (
        <>
            <AppContext.Provider value={{ devices }}>
                <div className="h-100 w-100" style={{ maxWidth: '70rem' }}>
                    <div className="flex flex-col items-center h-full md:w-12/12">
                        <div className="w-full">
                            <AppHeader />
                        </div>

                        <div
                            className="w-full flex-grow overflow-auto bg-white"
                            style={{ backgroundColor: '#1f263d' }}
                        >
                            <Switch>
                                <Route path="/commands">
                                    <Commands />
                                </Route>

                                <Route path="/devices">
                                    <Devices />
                                </Route>

                                <Route path="/tags">
                                    <Tags onControl={handleControl} />
                                </Route>

                                {/* <Route path="/devices/:id">
                                    <EditDevice
                                        onAddTag={handleAddTag}
                                        onRemoveTag={handleRemoveTag}
                                    />
                                </Route> */}


                                {/* <Route path="/search">
                                    <Search />
                                </Route> */}

                                {/* <Route path="/controls">
                                    <Controls onCommand={handleCommand} />
                                </Route> */}

                                <Route path="/">
                                    <Redirect to="/commands" />
                                </Route>
                            </Switch>
                        </div>

                        <div className="w-full">
                            <AppFooter />
                        </div>
                    </div>
                </div>
            </AppContext.Provider>
        </>
    );
}

export default App;
