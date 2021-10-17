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
    const sortIotDeviceGroup = (a: IotDeviceGroup, b: IotDeviceGroup) => (a.type > b.type ? 1 : -1);

    // Create the groups for the different type of devices.
    useEffect(() => {
        const groups: IotDeviceGroup[] = [];

        IotDeviceTypes.forEach((iotDeviceType) => {
            groups.push({
                type: iotDeviceType,
                devices: [],
            });
        });

        setIotDeviceGroups(groups.sort(sortIotDeviceGroup));
    }, []);

    // Insert all tags from all devices in a set, so to have only one value per tag.
    useEffect(() => {
        const allTags = new Set<string>();

        appContext.store.devices.forEach((device) => {
            if (device.tags) {
                device.tags.forEach((tag) => allTags.add(tag));
            }
        });

        setAllTags(Array.from(allTags).sort((a, b) => (a > b ? 1 : -1)));
    }, [appContext.store.devices]);

    // Filter devices that are missing the selected tags.
    useEffect(() => {
        const devices = appContext.store.devices.filter((device) => {
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
    }, [selectedTags, appContext.store.devices]);

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
        appContext.store.selectedGroup = iotDeviceGroup;
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
