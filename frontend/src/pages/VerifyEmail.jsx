import React, { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux';
import { Link, useLocation, useNavigate, useSearchParams } from 'react-router-dom'
import configureShowToast from '../components/showToast';
import { Box, Button, FormControl, FormLabel, Heading, Image, Input, ScaleFade, Spacer, Spinner, Text, useMediaQuery, useToast, VStack } from '@chakra-ui/react';
import CentredSpinner from '../components/CentredSpinner';
import colouredLogo from '/logo/svg/logo-color.svg';
import server from '../networking';

function VerifyEmail() {
    const navigate = useNavigate();
    const { state } = useLocation();
    const [searchParams] = useSearchParams();
    const [message, setMessage] = useState('Verifying...');
    const [messageColour, setMessageColour] = useState('black');
    const [messageHidden, setMessageHidden] = useState(true);
    const [codeInputHidden, setCodeInputHidden] = useState(true);
    const [verificationLoading, setVerificationLoading] = useState(false);
    const [limitedScreen] = useMediaQuery("(max-width: 800px)");
    const toast = useToast()
    const showToast = configureShowToast(toast);
    const dispatch = useDispatch();
    const { username, loaded, error } = useSelector(state => state.auth);
    const [code, setCode] = useState(searchParams.get('code') || '');
    const [userID, setUserID] = useState(searchParams.get('userID') || '');

    const buttonDisabled = !code || !userID;
    
    const handleCodeChange = (e) => { setCode(e.target.value); };
    const handleFieldEnter = () => { verifyOTP(); };
    const updateMessageField = (message, status) => {
        setMessage(message);
        setMessageHidden(false);
        
        if (status === 'error') {
            setMessageColour('red');
        } else if (status === 'success') {
            setMessageColour('green');
        } else {
            setMessageColour('black');
        }
    }

    const verifyOTP = () => {
        if (code.length !== 6) {
            updateMessageField('Invalid verification code', 'error');
            setCodeInputHidden(false);
            return;
        }

        setVerificationLoading(true);
    }

    useEffect(() => {
        var id = userID;
        if (state && state.userID) {
            setUserID(state.userID);
            id = state.userID;
        }

        if (!id) {
            showToast("Invalid verification link", 'Please try again.', 'error');
            navigate('/');
            return
        }
        if (!code) {
            setCodeInputHidden(false);
            return
        } else {
            verifyOTP();
        }
    }, [])

    if (!loaded) {
        return <CentredSpinner />
    }

    return (
        <Box display={'flex'} flexDirection={'column'} justifyContent={'center'} maxW={'100%'} p={!limitedScreen ? '10px' : '0px'}>
            <Box display={'flex'} flexDirection={'column'} justifyContent={'space-between'} alignItems={'center'} mt={!limitedScreen ? '10%' : '20%'}>
                <Spacer />
                <Link to={'/'}>
                    <Image src={colouredLogo} alt={'Logo'} maxH={'100px'} rounded={'xl'} />
                </Link>
                <Spacer />
                <Box display={'flex'} flexDir={'column'} justifyContent={'left'} alignItems={'center'} maxW={limitedScreen ? '70%' : '50%'} p={!limitedScreen ? '10px' : '0px'} mt={limitedScreen ? '20px' : '0px'}>
                    <ScaleFade in={true} initialScale={0.9}>
                        <Box display={'flex'} flexDir={'column'} alignItems={'center'}>
                            <Heading as={'h1'} size={'xl'}>Verify your email</Heading>
                            <VStack spacing={4} mt={10} hidden={codeInputHidden}>
                                <FormControl id='username' required>
                                    <FormLabel>Verification Code</FormLabel>
                                    <Input onKeyUp={handleFieldEnter} placeholder='Check your inbox' type='text' w={{ base: 'xs', md: 'md', lg: 'lg' }} value={code} onChange={handleCodeChange} disabled={verificationLoading} required />
                                </FormControl>
                            </VStack>
                            {verificationLoading && <Spinner />}
                            <VStack mt={'10%'} spacing={'20px'}>
                                <Text color={messageColour} hidden={messageHidden} >{message}</Text>
                                <Button variant={!buttonDisabled ? 'Default' : 'solid'} w={{ base: 'xs', md: 'md', lg: 'lg' }} onClick={verifyOTP} isDisabled={buttonDisabled} isLoading={verificationLoading}>Sign in</Button>
                            </VStack>
                        </Box>
                    </ScaleFade>
                </Box>
                <Spacer />
            </Box>
        </Box>
    )
}

export default VerifyEmail