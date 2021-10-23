import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faChevronUp, faChevronDown, faStopCircle } from '@fortawesome/free-solid-svg-icons';
import { Button } from '@components';

type Props = { onClick?: () => void; label?: string };

export function ButtonLabel(props: Props) {
    return (
        <Button
            onClick={props.onClick}
            content={props.label}
            colorClassBackground="bg-indigo-800"
            colorClassBackgroundFocus="bg-indigo-700"
        />
    );
}

export function ButtonOk(props: Props) {
    return (
        <Button
            onClick={props.onClick}
            content={<div className="px-4">OK</div>}
            colorClassBackground="bg-indigo-800"
            colorClassBackgroundFocus="bg-indigo-700"
        />
    );
}

export function ButtonAll(props: Props) {
    return (
        <Button
            onClick={props.onClick}
            content={<div className="w-14 text-2xl">All</div>}
            colorClassBackground="bg-indigo-800"
            colorClassBackgroundFocus="bg-indigo-700"
        />
    );
}

export function ButtonNone(props: Props) {
    return (
        <Button
            onClick={props.onClick}
            content={<div className="w-14 text-2xl">None</div>}
            colorClassBackground="bg-indigo-800"
            colorClassBackgroundFocus="bg-indigo-700"
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

export function ButtonBack(props: Props) {
    return (
        <Button
            onClick={props.onClick}
            content="Back"
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
            content="Edit"
            icon="chevron-right"
            colorClassBackground="bg-blue-700"
            colorClassBackgroundFocus="bg-blue-600"
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

export function ButtonOn(props: Props) {
    return (
        <Button
            onClick={props.onClick}
            content="ON"
            textSize="large"
            colorClassBackground="bg-green-800"
            colorClassBackgroundFocus="bg-green-700"
        />
    );
}

export function ButtonOff(props: Props) {
    return (
        <Button
            onClick={props.onClick}
            content="OFF"
            textSize="large"
            colorClassBackground="bg-red-800"
            colorClassBackgroundFocus="bg-red-700"
        />
    );
}
