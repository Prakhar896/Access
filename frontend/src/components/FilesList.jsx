import { Table, TableContainer, Tbody, Td, Text, Th, Thead, Tr, Link as ChakraLink, Button, Box, Spinner, useMediaQuery } from '@chakra-ui/react';
import { faCircleDown } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import React from 'react'

function FilesList({ filesData, retrieving }) {
    const backendURL = import.meta.env.VITE_BACKEND_URL;
    const [limitedScreen] = useMediaQuery("(max-width: 800px)");

    const downloadLinkFor = (file) => {
        return `${backendURL}/directory/file/${file}`;
    }

    if (retrieving == true) {
        return (
            <Box display={'flex'} justifyContent={'left'} alignItems={'center'} mt={'5%'}>
                <Spinner />
            </Box>
        )
    }

    if (!retrieving && filesData.length <= 0) {
        <Box display={'flex'} justifyContent={'left'} alignItems={'center'} mt={'5%'}>
            <Text>No files found.</Text>
        </Box>
    }

    console.log(filesData)

    return (
        <TableContainer mt={{ base: '15px', md: '20px', lg: '25px' }} w={limitedScreen && '100%'}>
            <Table variant='simple'>
                <Thead>
                    <Tr>
                        <Th>Name</Th>
                        {!limitedScreen && (
                            <>
                                <Th>Modified</Th>
                                <Th>Uploaded</Th>
                            </>
                        )}
                        <Th>Actions</Th>
                    </Tr>
                </Thead>
                <Tbody>
                    {filesData.map((file, index) => (
                        <Tr key={index}>
                            <Td>
                                <ChakraLink href={downloadLinkFor(file.name)} color={'blue.500'} fontSize={{ base: 'sm', md: 'md', lg: 'lg' }}><Text maxW={{ base: '200px', md: '300px', lg: 'fit-content' }} isTruncated>{file.name}</Text></ChakraLink>
                            </Td>
                            {!limitedScreen && (
                                <>
                                    <Td>{file.lastUpdate ?? "Unavailable"}</Td>
                                    <Td>{file.uploadedTimestamp}</Td>
                                </>
                            )}
                            <Td justifyContent={'center'}>
                                <Button onClick={() => { location.href = downloadLinkFor(file.name); }} variant={'ghost'} size={'md'}>
                                    <FontAwesomeIcon icon={faCircleDown} />
                                </Button>
                            </Td>
                        </Tr>
                    ))}
                </Tbody>
            </Table>
        </TableContainer>
    )
}

export default FilesList