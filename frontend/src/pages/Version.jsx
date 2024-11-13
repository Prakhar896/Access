import { Button, Text } from '@chakra-ui/react'
import React from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { changeSystemVersion } from '../slices/UniversalState';

function Version() {
    const dispatch = useDispatch();
    const Universal = useSelector(state => state.universal)

    const changeVersion = () => {
        dispatch(changeSystemVersion(prompt("Enter version:")))
    }

    return <>
        <Text>{Universal.systemVersion}</Text>
        <Button onClick={changeVersion}>Change</Button>
    </>
}

export default Version