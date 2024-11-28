import { Box, Card, CardBody, CardHeader, Heading, Spinner, Stack, StackDivider, Text, useMediaQuery, useToast } from '@chakra-ui/react'
import { useEffect, useState } from 'react'
import server from '../networking';
import configureShowToast from './showToast';

function AuditLogsList({ auditLogsData, retrievingAuditLogs }) {
    const [limitedScreen] = useMediaQuery("(max-width: 800px)");

    return (
        <Card ml={!limitedScreen && "20px"} mt={limitedScreen ? "20px" : "10px"} variant={'filled'}>
            <CardHeader>
                <Heading size='md'>Audit Logs</Heading>
            </CardHeader>

            <CardBody maxH={"400px"} overflow={"auto"}>
                {retrievingAuditLogs ? (
                    <>
                        <Spinner />
                        <Text>Retrieving...</Text>
                    </>
                ) : (
                    <Stack divider={<StackDivider />} spacing='4'>
                        {auditLogsData.map((log, index) => (
                            <Box key={index}>
                                <Heading size='xs' textTransform='uppercase'>
                                    {log.event}
                                </Heading>
                                <Heading size='xs' color='gray.500' textTransform='uppercase'>{log.timestamp}</Heading>
                                <Text pt='2' fontSize='sm'>
                                    {log.text}
                                </Text>
                            </Box>
                        ))}
                    </Stack>
                )}
            </CardBody>
        </Card>
    )
}

export default AuditLogsList