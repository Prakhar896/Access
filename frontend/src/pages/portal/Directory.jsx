import React, { useEffect, useState } from 'react'
import { Box, Button, Heading, Spacer, Spinner, Table, TableContainer, Tbody, Td, Text, Th, Thead, Tr, useDisclosure, useMediaQuery, useToast } from '@chakra-ui/react';
import { Link as ChakraLink } from '@chakra-ui/react';
import { useSelector } from 'react-redux';
import withAuth from '../../components/hoc/withAuth';
import withNavbar from '../../components/hoc/withNavbar';
import server from '../../networking';
import configureShowToast from '../../components/showToast';
import CentredSpinner from '../../components/CentredSpinner';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowDown, faArrowUpFromBracket, faCircleDown } from '@fortawesome/free-solid-svg-icons';
import FilesList from '../../components/FilesList';
import UploadFilesModal from '../../components/UploadFilesModal';

function Directory() {
    const { username, loaded } = useSelector(state => state.auth);
    const [filesData, setFilesData] = useState([]);
    const [retrievingFiles, setRetrievingFiles] = useState(true);
    const [limitedScreen] = useMediaQuery("(max-width: 800px)");
    const { isOpen: isUploadModalOpen, onOpen: onUploadModalOpen, onClose: onUploadModalClose } = useDisclosure();
    const toast = useToast();
    const showToast = configureShowToast(toast);

    const processFileData = (data) => {
        var newData = [];
        for (var file of data) {
            file["originalLastUpdate"] = structuredClone(file["lastUpdate"]);
            file["originalUploadedTimestamp"] = structuredClone(file["uploadedTimestamp"]);

            file["lastUpdate"] = file["lastUpdate"] ? new Date(file["lastUpdate"]).toLocaleString() : null;
            file["uploadedTimestamp"] = new Date(file["uploadedTimestamp"]).toLocaleString();

            newData.push(file);
        }

        return newData;
    }

    const fetchFiles = () => {
        server.get("/directory")
            .then(res => {
                if (res.status == 200) {
                    if (typeof res.data == "object" && !Array.isArray(res.data)) {
                        setFilesData(processFileData(Object.values(res.data)));
                        setRetrievingFiles(false);
                        return
                    } else {
                        console.log("Unexpected response format when retrieving files; response: ", res.data);
                    }
                } else {
                    console.log("Non-200 status code received in retrieving files; response: ", res.data);
                }
                showToast("Something went wrong", "Couldn't retrieves files. Please try again.", "error");
            })
            .catch(err => {
                if (err.response && err.response.data && typeof err.response.data == "string") {
                    if (err.response.data.startsWith("UERROR")) {
                        console.log("User error occurred in retrieving files; response: ", err.response.data);
                        showToast("Something went wrong", err.response.data.substring("UERROR: ".length), "error");
                        return
                    } else {
                        console.log("Unknown response from server in retrieving files; response: ", err.response.data);
                    }
                } else if (err.message && typeof err.message == "string") {
                    console.log("Error occurred in retrieving files; message: ", err.message);
                } else {
                    console.log("Unknown error occurred in retrieving files; error: ", err);
                }
                showToast("Something went wrong", "Couldn't retrieves files. Please try again.", "error");
            })
    }

    useEffect(() => {
        if (loaded) {
            fetchFiles();
        }
    }, [loaded]);

    useEffect(() => {
        console.log(filesData);
    }, [filesData]);

    return (
        <>
            <Box display={'flex'} flexDir={'column'} justifyContent={'left'} m={!limitedScreen ? '1rem' : '10px'} p={'10px'}>
                <Box display={'flex'} justifyContent={'left'} flexDirection={'row'} alignItems={'center'}>
                    <Heading as={'h1'} fontSize={'3xl'} fontFamily={'Ubuntu'}>My Files</Heading>
                    <Spacer />
                    <Button variant={'Default'} onClick={onUploadModalOpen}><FontAwesomeIcon icon={faArrowUpFromBracket} /></Button>
                </Box>
                <FilesList filesData={filesData} retrieving={retrievingFiles} triggerReload={fetchFiles} />
            </Box>
            <UploadFilesModal isOpen={isUploadModalOpen} onOpen={onUploadModalOpen} onClose={onUploadModalClose} triggerReload={fetchFiles} />
        </>
    )
}

export default withAuth(withNavbar(Directory));