import React, { useEffect, useState } from 'react'
import { Alert, AlertIcon, Box, Button, FormControl, FormLabel, Heading, Input, Spacer, Spinner, Text, useMediaQuery, useToast, VStack } from '@chakra-ui/react';
import configureShowToast from '../../components/showToast';
import { useSelector } from 'react-redux';
import server from '../../networking';

function MyAccount() {
    const { username, loaded } = useSelector(state => state.auth);
    const [limitedScreen] = useMediaQuery("(max-width: 800px)");

    const [profileData, setProfileData] = useState({});
    const [retrievingProfile, setRetrievingProfile] = useState(true);

    const toast = useToast();
    const showToast = configureShowToast(toast);

    const lastLoginDate = profileData.lastLogin ? new Date(profileData.lastLogin) : null;
    const creationDate = profileData.createdAt ? new Date(profileData.createdAt) : null;

    const getProfile = () => {
        server.post("/profile")
            .then(res => {
                if (res.status == 200 && typeof res.data == "object" && !Array.isArray(res.data)) {
                    setProfileData(res.data);
                    setRetrievingProfile(false);
                    return
                } else {
                    console.log("Non-200/unexpectedd response when retrieving profile; response: ", res.data);
                    showToast("Something went wrong", "Couldn't retrieve profile. Please try again.", "error");
                }
            })
            .catch(err => {
                if (err.response && err.response.data && typeof err.response.data == "string") {
                    if (err.response.data.startsWith("UERROR")) {
                        console.log("User error occurred in retrieving profile; response: ", err.response.data);
                        showToast("Something went wrong", res.data.substring("UERROR: ".length), "error");
                        return
                    } else {
                        console.log("Error occurred in retrieving profile; response: ", err.response.data);
                    }
                } else if (err.message && typeof err.message == "string") {
                    console.log("Error occurred in retrieving profile; message: ", err.message);
                } else {
                    console.log("Unknown error occurred in retrieving profile; error: ", err);
                }

                showToast("Something went wrong", "Couldn't retrieve profile. Please try again.", "error");
            })
    }

    useEffect(() => {
        if (loaded) {
            getProfile();
        }
    }, [])

    console.log(profileData)

    return (
        <Box display={'flex'} flexDir={'column'} justifyContent={'left'} m={!limitedScreen ? '1rem' : '10px'} p={'10px'}>
            <Box display={'flex'} justifyContent={'left'} flexDirection={'row'} alignItems={'center'}>
                <Heading as={'h1'} fontSize={'3xl'} fontFamily={'Ubuntu'}>My Account</Heading>
            </Box>

            <Box display={'flex'} justifyContent={'left'} flexDirection={'column'} alignItems={'left'} w={!limitedScreen ? '50%' : '100%'} mt={"5%"}>
                {retrievingProfile ? (
                    <Spinner />
                ) : (
                    <VStack spacing={"20px"}>
                        <FormControl>
                            <FormLabel><Text fontSize={'lg'}>Username</Text></FormLabel>
                            <Input value={profileData.username} isReadOnly />
                        </FormControl>
                        <FormControl>
                            <FormLabel><Text fontSize={'lg'}>Email</Text></FormLabel>
                            <Input type='email' value={profileData.email} isReadOnly />
                        </FormControl>
                        {profileData.emailVerified == false && (
                            <Alert status='warning' rounded={'xl'}>
                                <AlertIcon />
                                <Text fontSize={{ base: 'sm', md: 'md' }}>Verify your email to use many of Access' features.</Text>
                                <Spacer />
                                <Button colorScheme='yellow' variant={'outline'} fontSize={{ base: 'sm', md: 'md' }} p={'14px'}>Resend Code</Button>
                            </Alert>
                        )}
                        <FormControl>
                            <FormLabel><Text fontSize={'lg'}>Last login</Text></FormLabel>
                            <Text>{lastLoginDate?.toLocaleString('en-GB', { dateStyle: "long", timeStyle: "short", hour12: true }) || "Unavailable"}</Text>
                        </FormControl>
                        <FormControl>
                            <FormLabel><Text fontSize={'lg'}>Created on</Text></FormLabel>
                            <Text>{creationDate?.toLocaleString('en-GB', { dateStyle: "long", timeStyle: "short", hour12: true }) || "Unavailable"}</Text>
                        </FormControl>
                    </VStack>
                )}
            </Box>
        </Box>
    )
}

export default MyAccount;