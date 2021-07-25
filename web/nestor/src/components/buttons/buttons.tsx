import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
    faChevronUp,
    faChevronDown,
    faStopCircle,
} from '@fortawesome/free-solid-svg-icons';
import { Button } from '@components';

type Props = { onClick?: () => void; label?: string };

export function ButtonLabel(props: Props) {
    return (
        <Button
            onClick={props.onClick}
            content={props.label}
            colorClassBackground="bg-indigo-800"
            colorClassBackgroundFocus="bg-indigo-800"
        />
    );
}

export function ButtonOk(props: Props) {
    return (
        <Button
            onClick={props.onClick}
            content={<div className="px-4">OK</div>}
            colorClassBackground="bg-green-700"
            colorClassBackgroundFocus="bg-green-600"
        />
    );
}

export function ButtonCancel(props: Props) {
    return (
        <Button
            onClick={props.onClick}
            content="Cancel"
            colorClassBackground="bg-red-700"
            colorClassBackgroundFocus="bg-red-600"
        />
    );
}

export function ButtonPrevious(props: Props) {
    return (
        <Button
            onClick={props.onClick}
            content="Previous"
            icon="chevron-left"
            colorClassBackground="bg-blue-700"
            colorClassBackgroundFocus="bg-blue-600"
        />
    );
}

export function ButtonNext(props: Props) {
    return (
        <Button
            onClick={props.onClick}
            content="Next"
            icon="chevron-right"
            colorClassBackground="bg-blue-700"
            colorClassBackgroundFocus="bg-blue-600"
        />
    );
}

export function ButtonDelete(props: Props) {
    return (
        <Button
            onClick={props.onClick}
            content="Delete"
            colorClassBackground="bg-gray-900"
            colorClassBackgroundFocus="bg-gray-800"
        />
    );
}

export function ButtonRemove(props: Props) {
    return (
        <Button
            onClick={props.onClick}
            content="Remove"
            colorClassBackground="bg-gray-900"
            colorClassBackgroundFocus="bg-gray-800"
        />
    );
}

export function ButtonEdit(props: Props) {
    return (
        <Button
            onClick={props.onClick}
            content={<div className="px-4">Edit</div>}
            colorClassBackground="bg-indigo-800"
            colorClassBackgroundFocus="bg-indigo-700"
        />
    );
}

export function ButtonDetail(props: Props) {
    return (
        <Button
            onClick={props.onClick}
            content="Detail"
            icon="arrow-right"
            colorClassBackground="bg-indigo-800"
            colorClassBackgroundFocus="bg-indigo-700"
        />
    );
}

export function ButtonBigUp(props: Props) {
    return (
        <Button
            onClick={props.onClick}
            content={
                <FontAwesomeIcon
                    className="m-1"
                    style={{ width: '6rem' }}
                    icon={faChevronUp}
                    size="4x"
                />
            }
            colorClassBackground="bg-yellow-600"
            colorClassBackgroundFocus="bg-yellow-500"
        />
    );
}

export function ButtonBigDown(props: Props) {
    return (
        <Button
            onClick={props.onClick}
            content={
                <FontAwesomeIcon
                    className="m-1"
                    style={{ width: '6rem' }}
                    icon={faChevronDown}
                    size="4x"
                />
            }
            colorClassBackground="bg-yellow-600"
            colorClassBackgroundFocus="bg-yellow-500"
        />
    );
}

export function ButtonBigStop(props: Props) {
    return (
        <Button
            onClick={props.onClick}
            content={
                <FontAwesomeIcon
                    className="m-1"
                    style={{ width: '6rem' }}
                    icon={faStopCircle}
                    size="4x"
                />
            }
            colorClassBackground="bg-yellow-600"
            colorClassBackgroundFocus="bg-yellow-500"
        />
    );
}