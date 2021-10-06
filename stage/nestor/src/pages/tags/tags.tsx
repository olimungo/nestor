import styles from './tags.module.css';
import { useContext, useEffect, useState } from 'react';
import {
    AppContext,
    DeviceTypes,
    getDeviceTypeLabel,
    getDeviceTypeCode,
    DevicesByTagsType,
} from '@declarations';
import { Tag, DeviceByTags } from '@components';

type Props = { onControl?: (selectedDevices: DevicesByTagsType) => void };

export function Tags(props: Props) {
    const dummyCallback = () => true;
    const { onControl = dummyCallback } = props;
    const appContext = useContext(AppContext);
    const [allTags, setAllTags] = useState<string[]>([]);
    const [selectedTags, setSelectedTags] = useState<string[]>([]);
    const [devicesByTags, setDevicesByTags] = useState<DevicesByTagsType[]>([]);

    useEffect(() => {
        const devicesByTags: DevicesByTagsType[] = [];

        for (const value in DeviceTypes) {
            if (!isNaN(Number(value))) {
                const id = Number(value);
                const code = getDeviceTypeCode(id);
                const label = getDeviceTypeLabel(id);
                devicesByTags.push({
                    id,
                    code,
                    label,
                    devices: [],
                });
            }
        }

        console.log(devicesByTags)

        setDevicesByTags(
            devicesByTags.sort((a, b) => (a.code > b.code ? 1 : -1))
        );
    }, []);

    useEffect(() => {
        if (appContext.devices && appContext.devices.length > 0) {
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
            const devices = appContext.devices.filter((device) => {
                // Filter devices that are missing the selected tags
                const remainingTags = selectedTags.filter(
                    (selectedTag) =>
                        device.tags.findIndex((tag) => tag === selectedTag) ===
                        -1
                );

                if (remainingTags.length > 0) {
                    return false;
                }

                return true;
            });

            setDevicesByTags((devicesByTags) => {
                const newDevicesByTags = [...devicesByTags];

                newDevicesByTags.forEach((deviceByTags) => {
                    deviceByTags.devices = [];
                });

                devices.forEach((device) => {
                    newDevicesByTags.forEach((deviceByTags) => {
                        if (deviceByTags.code === device.type) {
                            deviceByTags.devices.push(device);
                        }
                    });
                });

                return newDevicesByTags;
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
            setSelectedTags((selectedTags) =>
                selectedTags.filter((tag) => tag !== label)
            );
        }
    };

    return (
        <div className={`${styles.component}`}>
            <div className="flex flex-wrap">
                {allTags.map((tag) => (
                    <Tag key={tag} label={tag} onClick={handleTagClicked} />
                ))}
            </div>

            {devicesByTags.map((deviceByTags) => (
                <DeviceByTags
                    key={deviceByTags.id}
                    devicesByTags={deviceByTags}
                    onControl={onControl}
                />
            ))}
        </div>
    );
}
