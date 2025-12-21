/*
 * protocol.h
 *
 *  Created on: Dec 14, 2025
 *      Author: yehui
 */

#ifndef INC_PROTOCOL_H_
#define INC_PROTOCOL_H_

extern int protocol_current_rx_buff_idx;

void protocol_process_received_frame(void);
void protocol_start_receive_host(void);

#endif /* INC_PROTOCOL_H_ */
