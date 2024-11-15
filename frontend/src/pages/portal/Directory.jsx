import React from 'react'
import withAuth from '../../components/withAuth'
import { Text } from '@chakra-ui/react';
import { useSelector } from 'react-redux';

function Directory() {
    const { username } = useSelector(state => state.auth);

    return (
        <Text>Welcome {username}!</Text>
    )
}

export default withAuth(Directory);