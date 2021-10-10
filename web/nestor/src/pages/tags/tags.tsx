import styles from './tags.module.css';
import { useContext, useEffect, useState } from 'react';
import { AppContext, IotDeviceTypes, IotDeviceGroup } from '@models';
import { Tag, DeviceGroup } from '@components';
import { useHistory } from 'react-router-dom';

export function Tags() {
    const appContext = useContext(AppContext);
    const history = useHistory();
    const [allTags, setAllTags] = useState<string[]>([]);
    const [selectedTags, setSelectedTags] = useState<string[]>([]);
    const [iotDeviceGroups, setIotDeviceGroups] = useState<IotDeviceGroup[]>([]);

    useEffect(() => {
        const groups: IotDeviceGroup[] = [];

        // Create the groups for the different type of devices.
        IotDeviceTypes.forEach((iotDeviceType) => {
            groups.push({
                type: iotDeviceType,
                devices: [],
            });
        });

        setIotDeviceGroups(groups.sort((a, b) => (a.type > b.type ? 1 : -1)));
    }, []);

    useEffect(() => {
        if (appContext.devices && appContext.devices.length > 0) {
            // Insert all tags from all devices in a set, so to have only one value per tag.
            const allTags = new Set<string>();

            appContext.devices.forEach((device) => {
                if (device.tags) {
                    device.tags.forEach((tag) => allTags.add(tag));
                }
            });

            setAllTags(Array.from(allTags).sort((a, b) => (a > b ? 1 : -1)));
        }
    }, [appContext.devices]);

    useEffect(() => {
        if (appContext.devices && appContext.devices.length > 0) {
            // Filter devices that are missing the selected tags.
            const devices = appContext.devices.filter((device) => {
                const remainingTags = selectedTags.filter(
                    (selectedTag) => device.tags.findIndex((tag) => tag === selectedTag) === -1
                );

                return remainingTags.length === 0;
            });

            setIotDeviceGroups((iotDeviceGroups) => {
                const newIotDeviceGroups = [...iotDeviceGroups];

                newIotDeviceGroups.forEach((iotDeviceGroup) => {
                    iotDeviceGroup.devices = [];
                });

                devices.forEach((device) => {
                    newIotDeviceGroups.forEach((iotDeviceGroup) => {
                        if (iotDeviceGroup.type === device.type) {
                            iotDeviceGroup.devices.push(device);
                        }
                    });
                });

                return newIotDeviceGroups;
            });
        }
    }, [selectedTags, appContext.devices]);

    const handleTagClicked = (label: string) => {
        // Check if tag was already selected
        const index = selectedTags.findIndex((tag) => tag === label);

        if (index === -1) {
            // If not already selected, add it to the array
            setSelectedTags((selectedTags) => [...selectedTags, label]);
        } else {
            // If already selected, remove it from the array
            setSelectedTags((selectedTags) => selectedTags.filter((tag) => tag !== label));
        }
    };

    const handleGroupSelected = (iotDeviceGroup: IotDeviceGroup) => {
        appContext.selectedGroup = iotDeviceGroup;
        history.push('/controls');
    };

    return (
        <div className={`${styles.component}`}>
            <div className="flex flex-wrap">
                {allTags.map((tag) => (
                    <Tag key={tag} label={tag} enableClick={true} onClick={handleTagClicked} />
                ))}
            </div>

            {iotDeviceGroups.map((iotDeviceGroup) => (
                <DeviceGroup
                    key={iotDeviceGroup.type}
                    iotDeviceGroup={iotDeviceGroup}
                    onSelected={handleGroupSelected}
                />
            ))}
        </div>
    );
}
